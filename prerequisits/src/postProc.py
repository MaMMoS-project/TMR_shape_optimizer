import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
import pandas as pd 
import logging
import matplotlib
import logging

from prerequisits.src.results import *


# -----------do not modify below this line----------------

#This class is used to load data from a file and perform a linear regression on the data
# The linear regression is performed of the hysteresis loop date from 0 to the threshhold_training
# Then all the data which in inbetrween the margin_to_line is assumed to have linear behaviour

class PostProc:
    def __init__(self, threshhold_training, margin_to_line, m_guess = 1, shape = None, iter = -1): 
        # starting from 0 on how much data will be used for training the linear regression of middel part of hysteresis loop
        # if choosen too high hysteresis loop wont have linear behaviour
        self.threshhold_training = threshhold_training
        #value of h_ex at which the training data ends
        self.h_threshhold_training = None
        

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

        #logger
        self.logger = logging.getLogger(__name__)

        #shape of the selsor/object
        self.shape = shape

        # try to get shape information. However to enable singe posprocess independent from sin cycle empy shape is possible...
        try:
            self.shape_info = self.shape.get_info_shape()
            self.schape_name = self.shape.get_project_name()
        except:
            self.shape_info = ["unknowen shape", "unknowen shape", "unknowen shape"]
            self.schape_name = "unknowen shape"

        
        #try to get the iteration number
        self.iter = iter
        



        


    def load_file(self, location,  iter, simulation, project_Name):
        #--------load file----------------
        

        file_path = os.path.join(location, f"output/{iter}/main/slurm_{simulation.get_main_SlurmID()}/{project_Name}.dat")
        self.logger.debug(f"Loading file {file_path}")

        
        # Check if the file exists  or not
        if not os.path.exists(file_path):
            self.logger.error(f'[Error]: File {file_path} does not exist')

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
                    self.logger.error(f'[Error]: Expected 3 columns, got {len(numbers)}')
                # Convert the numbers to floats
                numbers = [float(number) for number in numbers]
                self.data = np.vstack((self.data, numbers))

        
        if not self.data.shape[0] > 5:
            self.logger.error(f'[Error]: Expected at least 5 rows, got {self.data.shape[0]}')
        

        #--------extrtact data----------------
                

        # Extract columns 2 and 3 from the data
        self.df = pd.DataFrame(self.data, columns=['time', 'H_ex', 'M'])


        #for taining only consider points with m < threshhold
        #this way we can see how long the mag stays linear
        self.h_threshhold_training = self.df['H_ex'].iloc[np.argmin(np.abs(self.df['M'] - self.threshhold_training))]
        self.df_training = self.df[self.df['H_ex'] < self.h_threshhold_training]
        self.df_training = self.df_training[self.df_training['M'] >= 0]

    
    def load_file_singe(self, file_path):
        #--------load file----------------
        

        self.logger.debug(f"Loading file {file_path}")

        
        # Check if the file exists  or not
        if not os.path.exists(file_path):
            self.logger.error(f'[Error]: File {file_path} does not exist')

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
                    self.logger.error(f'[Error]: Expected 3 columns, got {len(numbers)}')
                # Convert the numbers to floats
                numbers = [float(number) for number in numbers]
                self.data = np.vstack((self.data, numbers))
    
        
        if not self.data.shape[0] > 5:
            self.logger.error(f'[Error]: Expected at least 5 rows, got {self.data.shape[0]}')
        

        #--------extrtact data----------------
        self.extract_data()
                
    def extract_data(self, index_adjustment=0):
        """
        Extracts data from the given dataset for fitting only.

        Parameters:
        - index_adjustment (int): The adjustment value for the index.
                                If fitting is not working, raise the value to try a different part for the linear regression.

        Returns:
        None
        """

        # Extract columns 2 and 3 from the data
        self.df = pd.DataFrame(self.data, columns=['time', 'H_ex', 'M'])

        # For training, only consider certain points:
        try:
            # Determine the upper boundary for training data
            upper_index = index_adjustment + np.argmin(np.abs(self.df['M'] - self.threshhold_training))
            self.h_threshhold_training = self.df['H_ex'].iloc[upper_index]
            
            # Filter the data for the training set
            self.df_training = self.df[self.df['H_ex'] < self.h_threshhold_training]

            # Determine the lower boundary for training data
            lower_index = index_adjustment + np.argmin(np.abs(self.df['M'] >= 0))
            self.h_threshhold_training_lowerbound = self.df['H_ex'].iloc[lower_index]
            
            # Further filter the training set based on the lower boundary
            self.df_training = self.df_training[self.df_training['H_ex'] >= self.h_threshhold_training_lowerbound]
        except Exception as e:
            self.logger.error(f'[ERROR]: Could not extract data with index_adjustment of {index_adjustment}: {e}')
            raise ValueError('Skip Postprocessing')

        

    #----------- compute linear regression----------------
    # Fixed point through which the regression line should pass
    def linear_regression(self, regression_restart_counter):
        """
        Performs linear regression on the given data points.

        Args:
            regression_restart_counter (int): The number of times the regression has been restarted.

        Raises:
            ValueError: If there are less than 10 points in the margin for linear regression.
            ValueError: If the optimization did not converge.
            ValueError: If the optimization is suspiciously inaccurate.
            ValueError: If the slope is not within a reasonable range.

        Returns:
            None
        """

        # quadratic penalty function
        def penalty_function(m, x, y, b = 0):
            #print(y.iloc[index_closest_to_zero])
            return np.sum((y - PostProc.line(x=x, m=m, b=b)) ** 2)
        
        
        #self.df_training = self.df[self.df['M'] >= 0].tail(margin_to_line)
        # test if linear regression is possible
        if self.df_training.shape[0] < 10:
            self.logger.error(f'[ERROR]: Less than 10 points in margin [0,{self.threshhold_training}] for linear regression, either generate more datapoint od rise margin')
            raise ValueError(f'Skip Postprocessing')
        #for taining only consider points with 0 <= m < threshhold
        #this way we can see how long the mag stays linear
        
    


        self.results.set_b(self.df_training['M'].iloc[np.argmin(np.abs(self.df_training['H_ex']))])

        res = minimize(penalty_function, self.m_guess, args=(self.df_training['H_ex'], self.df_training['M'], self.results.get_b()))
        self.results.set_res_of_optimization(res)
        print(res)

        # Test is the linear regression has worked:
        #break if not converged
        if not res.success:
            self.logger.error(f'Optimization did not converge in general: {res.message}')
            raise ValueError(f'Skip Postprocessing')
        
        # breakt accuracy is not good enough
        if not res.success:
            self.logger.error(f'[ERROR]: Optimization is suspiciusly unaccuract: {res.fun}, check .dat for bad hysteresis loop')
            if regression_restart_counter < 10:
                # Restart the regression with a index_adjustment
                # there migt be a jump in the demag curve and we will try to avoid it
                self.logger.error(f'[INFO]: Restarting regression with index_adjustment = {regression_restart_counter}')
                self.extract_data(index_adjustment=regression_restart_counter**2)
                self.linear_regression(regression_restart_counter + 1)
            raise ValueError(f'Skip Postprocessing')
        # breat if slope is odd
        if not res.x > 0 and res.x < 1000:
            self.logger.error(f'[ERROR]: Slope is not reasonable: {res.x}')
            raise ValueError(f'Skip Postprocessing')

        self.results.set_res_of_optimization(res)
    
    @staticmethod
    def line(x, m, b = 0):
        return m * x + b
    
    #analyse the hysteresis loop
    def anasyse_data(self):
        # Extract the optimal value of m
        self.m_calc = self.results.get_res_of_optimization().x
        self.b = self.results.get_b()


        self.results.set_slope(self.m_calc)

        number_points_in_margin = np.sum(np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) < self.margin_to_line)
        self.results.set_number_points_in_margin(number_points_in_margin)

        x_max_lin = np.max(self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) < self.margin_to_line]) 
        self.results.set_x_max_lin(x_max_lin)

        # test if the linear behaviour reasanable
        if not x_max_lin > 0:
            self.logger.error(f'[ERROR]: Linear behaviour is not reasonable: {x_max_lin}')
            raise ValueError(f'Skip Postprocessing')
        if not number_points_in_margin > 8 :
            self.logger.error(f'[ERROR]: Number of points in margin is not reasonable: {number_points_in_margin}')
            raise ValueError(f'Skip Postprocessing')

    def get_x_max_lin(self):
        return self.results.get_x_max_lin()      

    def get_results(self):
        return self.results  

    # Do not perform in automization just for testing
    def plot_data(self):



        #x values 
        x_reg = np.linspace(self.df['H_ex'].min(), self.df['H_ex'].max(), 500)

        #calc number of points in the data wich are as close to calculated regression by threshhold
        #this is to see how well the regression fits the data

        #print(self.df['H_ex'])
        print(self.m_calc)
        

        x_in_margin = self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) < self.margin_to_line]
        y_in_margin = self.df['M'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) < self.margin_to_line]
        x_of_margin = self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) >= self.margin_to_line]
        y_of_margin = self.df['M'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) >= self.margin_to_line]

        y_reg = PostProc.line(x_reg, self.m_calc, self.b)
        y_margin_low = PostProc.line(x_reg, self.m_calc  , - self.margin_to_line + self.b)
        y_margin_high = PostProc.line(x_reg, self.m_calc , + self.margin_to_line + self.b)

        

        print(f'Distance in margin: {self.results.get_x_max_lin():.2f}')




        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter(x_in_margin, y_in_margin, color='green', label='Data Points in Margin' ) 
        plt.scatter(x_of_margin, y_of_margin, color='red', label='Data Points out of Margin' )
        plt.plot(x_reg, y_reg, color='red', label=f'Regression Line: m = {self.m_calc[0]:.2f}x b = {self.results.get_b()} ')
        plt.axvline(self.results.get_x_max_lin(), color='black', linestyle='--', label=f'Distance with lin behavior: {np.max(x_in_margin)}')
        plt.plot(x_reg, y_margin_low, color='green', linestyle='--', label=f'Lower Margin: m = {self.m_calc[0]:.2f}x b = {-self.margin_to_line} ')
        plt.plot(x_reg, y_margin_high, color='green', linestyle='--', label=f'Upper Margin: m = {self.m_calc[0]:.2f}x b = {+ self.margin_to_line} ')
        plt.axvline(0, color='black', linestyle='--')
        plt.xlabel('$H_{ex}$')
        plt.ylabel('$m_y$')
        plt.title(f'Iteration: {self.iter} Shape: {self.schape_name} Shape Info: {self.shape_info}')

        plt.legend()


        plt.show()
        plt.close()

    def save_plot(self, location, iter, full_path = True):
        #x values 
        x_reg = np.linspace(self.df['H_ex'].min(), self.df['H_ex'].max(), 500)

        #calc number of points in the data wich are as close to calculated regression by threshhold
        #this is to see how well the regression fits the data

        #print(self.df['H_ex'])
        print(self.m_calc)
        
        x_in_margin = self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) < self.margin_to_line]
        y_in_margin = self.df['M'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) < self.margin_to_line]
        x_of_margin = self.df['H_ex'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) >= self.margin_to_line]
        y_of_margin = self.df['M'][np.abs(self.df['M'] - PostProc.line(self.df['H_ex'], self.m_calc, self.b)) >= self.margin_to_line]

        y_reg = PostProc.line(x_reg, self.m_calc, self.b)
        y_margin_low = PostProc.line(x_reg, self.m_calc  , - self.margin_to_line + self.b)
        y_margin_high = PostProc.line(x_reg, self.m_calc , + self.margin_to_line + self.b)

        

        #print(f'Distance in margin: {self.results.get_x_max_lin():.2f}')




        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter(x_in_margin, y_in_margin, color='green', label='Data Points in Margin' ) 
        plt.scatter(x_of_margin, y_of_margin, color='red', label='Data Points out of Margin' )
        plt.plot(x_reg, y_reg, color='red', label=f'Regression Line: m = {self.m_calc[0]:.2f}x b = {self.results.get_b()} ')
        plt.axvline(self.results.get_x_max_lin(), color='black', linestyle='--', label=f'Distance with lin behavior: {np.max(x_in_margin)}')
        plt.plot(x_reg, y_margin_low, color='green', linestyle='--', label=f'Lower Margin: m = {self.m_calc[0]:.2f}x b = {-self.margin_to_line} ')
        plt.plot(x_reg, y_margin_high, color='green', linestyle='--', label=f'Upper Margin: m = {self.m_calc[0]:.2f}x b = {+ self.margin_to_line} ')
        plt.axvline(0, color='black', linestyle='--')
        plt.xlabel('H_ex')
        plt.ylabel('M')
        plt.title(f'Iteration: {self.iter} Shape: {self.schape_name} Shape Info: {self.shape_info}')

        plt.legend()

        # save localy for sim or global for db
        if full_path:
            file_path = os.path.join(location, f"output/graphics/{iter}.png") 
        else:
            file_path = os.path.join(location, f"{iter}.png")

        plt.savefig(file_path)
        plt.close()
        self.logger.debug(f"Saved plot to {file_path}")

    




