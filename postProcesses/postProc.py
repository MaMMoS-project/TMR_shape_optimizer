import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
import pandas as pd 

from results import Results


# -----------do not modify below this line----------------

#This class is used to load data from a file and perform a linear regression on the data
# The linear regression is performed of the hysteresis loop date from 0 to the threshhold_training
# Then all the data which in inbetrween the margin_to_line is assumed to have linear behaviour

class PostProc:
    def __init__(self, threshhold_training, margin_to_line, m_guess = 1): 
        # starting from 0 on how much data will be used for training the linear regression of middel part of hysteresis loop
        # if choosen too high hysteresis loop wont have linear behaviour
        self.threshhold_training = threshhold_training

        # margin to line is the distance between the regression line and the data points with linear behaviour
        self.margin_to_line = margin_to_line

        # initial guess for the slope of the regression line does not real matter
        self.m_guess = m_guess

        # data is loaded from the file
        self.data = None

        #data which is used for training the lin regression
        self.df_training = None

        #results of the post processing
        self.results = Results()


        


    def load_file(self, file_path):
        #--------load file----------------
        #TODO: paths must be adjusted in automatizatiuon process
        POSTPROCESSES_DIR = Path('postProcesses').resolve()

        # Specify the file path
        file_path = POSTPROCESSES_DIR.joinpath(file_path)


        # Check if the file exists  or not
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'[Error]: File {file_path} does not exist')

        # Read the file 
        self.data = np.empty((0, 3))

        # Open the file
        with open(file_path, 'r') as file:
            # Read the file line by line
            for line in file:
                #check if line is empty
                if line.strip() == '':
                    continue
                #cheack if data was read properly
                
                numbers = line.strip().split()
                if len(numbers) != 3:
                    raise ValueError(f'[Error]: Expected 3 columns, got {len(numbers)}')
                # Convert the numbers to floats
                numbers = [float(number) for number in numbers]
                self.data = np.vstack((self.data, numbers))

        
        if not self.data.shape[0] > 5:
            raise ValueError(f'[Error]: Expected at least 5 rows, got {self.data.shape[0]}')
        

        #--------extrtact data----------------
                

        # Extract columns 2 and 3 from the data
        self.df = pd.DataFrame(self.data, columns=['time', 'H_ex', 'M'])


        #for taining only consider points with m < threshhold
        #this way we can see how long the mag stays linear
        self.df_training = self.df[self.df['M'] < threshhold_training]

    #----------- compute linear regression----------------
    # Fixed point through which the regression line should pass
    def linear_regression(self):
        

        # quadratic penalty function
        def penalty_function(m, x, y):
            return np.sum((y - PostProc.line(x, m)) ** 2)




        # Call the minimizer
        res = minimize(penalty_function, m_guess, args=(self.df_training['H_ex'], self.df_training['M']))

        #break if not converged
        if not res.success:
            raise RuntimeError(f'[ERROR]: Optimization did not converge in general: {self.res.message}')
        
        # breakt accuracy is not good enough
        if not res.fun < self.margin_to_line:
            self.plot_data()
            raise RuntimeError(f'[ERROR]: Optimization is suspiciusly unaccuract: {self.res.fun}, check .dat for bad hysteresis loop')

        self.results.set_res_of_optimization(res)
    
    @staticmethod
    def line(x, m, b = 0):
            return m * x + b
    
    #analyse the hysteresis loop
    def anasyse_data(self):
        # Extract the optimal value of m
        m_calc = self.results.get_res_of_optimization().x

        self.results.set_slope(m_calc)

        number_points_in_margin = np.sum(np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], m_calc)) < margin_to_line)
        self.results.set_number_points_in_margin(number_points_in_margin)

        x_max_lin = np.max(self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], m_calc)) < margin_to_line]) 
        self.results.set_x_max_lin(x_max_lin)





        


    # Do not perform in automization just for testing
    def plot_data(self):

        m_calc = self.results.get_slope()

        #x values 
        x_reg = np.linspace(self.df['H_ex'].min(), self.df['H_ex'].max(), 500)

        #calc number of points in the data wich are as close to calculated regression by threshhold
        #this is to see how well the regression fits the data
        

        x_in_margin = self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], m_calc)) < margin_to_line]
        y_in_margin = self.df['M'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], m_calc)) < margin_to_line]
        x_of_margin = self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], m_calc)) >= margin_to_line]
        y_of_margin = self.df['M'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], m_calc)) >= margin_to_line]

        y_reg = PostProc.line(x_reg, m_calc)
        y_margin_low = PostProc.line(x_reg, m_calc  , - margin_to_line)
        y_margin_high = PostProc.line(x_reg, m_calc , + margin_to_line)

        

        print(f'Distance in margin: {self.results.get_x_max_lin():.2f}')




        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter(x_in_margin, y_in_margin, color='green', label='Data Points in Margin: ' + str(self.results.get_x_max_lin()), ) 
        plt.scatter(x_of_margin, y_of_margin, color='red', label='Data Points out of Margin: ' + str(len(x_of_margin)))
        plt.plot(x_reg, y_reg, color='red', label=f'Regression Line: m = {m_calc[0]:.2f}x b = 0 ')
        plt.axvline(np.max(x_in_margin), color='black', linestyle='--', label=f'End of Margin: {np.max(x_in_margin):.2f}')
        plt.plot(x_reg, y_margin_low, color='green', linestyle='--', label=f'Lower Margin: m = {m_calc[0]:.2f}x b = {-margin_to_line} ')
        plt.plot(x_reg, y_margin_high, color='green', linestyle='--', label=f'Upper Margin: m = {m_calc[0]:.2f}x b = {+ margin_to_line} ')
        plt.xlabel('H_ex')
        plt.ylabel('M')
        plt.title('Data Plot')

        plt.legend()


        plt.show()




#----------Modify parameters----------------
# Set the threshold for the training data
# Only consider points with M < threshold for training
# This will help us see how long the magnetization stays linear
threshhold_training = .1


# Set the margin in wich 
margin_to_line = 0.05

# Initial guess for m in the regression line
m_guess = 3



# ----------- end of parameters----------------

temp_post = PostProc(threshhold_training, margin_to_line, m_guess)
temp_post.load_file('tmr_sensor_MEMS_fundations_postpro.dat')
temp_post.linear_regression()
temp_post.anasyse_data()
temp_post.plot_data()

