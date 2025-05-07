import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
import pandas as pd 
from prerequisits.src.configuration import OptimizerConfig
from prerequisits.src.shape import Shape
from prerequisits.src.AbstractPostProc import AbstractPostProc

class MinSlopePostProc(AbstractPostProc):
    """
    Implementation of AbstractPostProc for post-processing simulation data,
    extending functionalities from the previous PostProc class.
    """
    
    def __init__(self, shape: Shape = None,  threshhold_training: float = 0.5, margin_to_line: float = 0.1, m_guess: float = 3.0):
        super().__init__( shape)
        self.threshhold_training = threshhold_training
        self.margin_to_line = margin_to_line
        self.m_guess = m_guess
        self.h_threshhold_training = None
        self.data = None
        self.df_training = None
        self.regression_restart_counter = 0
        #result of Linregression
        self.res = None
        # offset of hysteresis
        self.b = 0
        # slope of hysteresis
        self.m = 0

        # try to get shape information. However to enable singe posprocess independent from sin cycle empy shape is possible...
        try:
            self.shape_info = self.shape.get_info_shape()
            self.schape_name = self.shape.get_project_name()
        except:
            self.shape_info = ["unknowen shape", "unknowen shape", "unknowen shape"]
            self.schape_name = "unknowen shape"

        
        #try to get the iteration number
        self.iter = iter


    
    
    def calc_label(self) -> float:
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
            return np.sum((y - MinSlopePostProc.line(x=x, m=m, b=b)) ** 2)
        
        
        #self.df_training = self.df[self.df['M'] >= 0].tail(margin_to_line)
        # test if linear regression is possible
        if self.df_training.shape[0] < 10:
            self.logger.error(f'[ERROR]: Less than 10 points in margin [0,{self.threshhold_training}] for linear regression, either generate more datapoint od rise margin')
            raise ValueError(f'Skip Postprocessing')
        #for taining only consider points with 0 <= m < threshhold
        #this way we can see how long the mag stays linear
        
    


        self.b = (self.df_training['M'].iloc[np.argmin(np.abs(self.df_training['H_ex']))])

        self.res = minimize(penalty_function, self.m_guess, args=(self.df_training['H_ex'], self.df_training['M'], self.b))
        
        self.m = self.res.x[0]
        #print(res)

        # Test is the linear regression has worked:
        #break if not converged
        if not self.res.success:   
            self.logger.error(f'Optimization did not converge in general: {self.res.message}')
            raise ValueError(f'Skip Postprocessing')
        
        # breakt accuracy is not good enough
        if not self.res.success:   #TODO: configure with actuall accuracy
            self.logger.error(f'[ERROR]: Optimization is suspiciusly unaccuract: {self.res.fun}, check .dat for bad hysteresis loop')
            if self.regression_restart_counter < 10:
                # Restart the regression with a index_adjustment
                # there migt be a jump in the demag curve and we will try to avoid it
                self.logger.error(f'[INFO]: Restarting regression with index_adjustment = {self.regression_restart_counter}')
                self.extract_data(index_adjustment=self.regression_restart_counter**2)
                self.calc_label(self.regression_restart_counter + 1)
            raise ValueError(f'Skip Postprocessing')
        # breat if slope is odd
        if not self.res.x[0] > 0 and self.res.x[0] < 1000:
            self.logger.error(f'[ERROR]: Slope is not reasonable: {self.res.x[0]}')
            raise ValueError(f'Skip Postprocessing')

        return self.calc_lin_dis()
    
    @staticmethod
    def line(x, m, b = 0):
        return m * x + b
    
    def calc_lin_dis(self):

        deviation = np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.m, self.b))
        in_margin = deviation < self.margin_to_line

        # Count total in-margin points (could include multiple groups)
        self.number_points_in_margin = np.sum(in_margin)

        # Find the index where the first deviation occurs (first False in in_margin)
        first_break_idx = np.argmax(~in_margin.values)

        # Get the last index before the break
        last_in_margin_idx = first_break_idx - 1 if first_break_idx > 0 else None

        # Validate
        if last_in_margin_idx is None:
            self.logger.error(f'[ERROR]: No initial linear region detected')
            raise ValueError('Skip Postprocessing')

        self.x_max_lin = self.df['H_ex'].iloc[last_in_margin_idx]

        if not self.x_max_lin > 0:
            self.logger.error(f'[ERROR]: Linear behaviour is not reasonable: {self.x_max_lin}')
            raise ValueError('Skip Postprocessing')

        if not self.number_points_in_margin > 8:
            self.logger.error(f'[ERROR]: Number of points in margin is not reasonable: {self.number_points_in_margin}')
            raise ValueError('Skip Postprocessing')

        


        
        return self.x_max_lin
    
    def plot_postProc(self):

        if self.df is None:
            self.logger.error(f'[ERROR]: Trying to plot but No data loaded')
            raise ValueError(f'Skip Postprocessing')
        # Make sure the label has been calculated
        if self.res is None:
            self.calc_label()

        #x values 
        x_reg = np.linspace(self.df['H_ex'].min(), self.df['H_ex'].max(), 500)

        #calc number of points in the data wich are as close to calculated regression by threshhold
        #this is to see how well the regression fits the data

        #print(self.df['H_ex'])
        print(self.res.x[0])
        

        x_in_margin = self.df['H_ex'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) < self.margin_to_line]
        y_in_margin = self.df['M'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) < self.margin_to_line]
        x_of_margin = self.df['H_ex'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) >= self.margin_to_line]
        y_of_margin = self.df['M'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) >= self.margin_to_line]

        y_reg = MinSlopePostProc.line(x_reg, self.res.x[0], self.b)
        y_margin_low = MinSlopePostProc.line(x_reg, self.res.x[0]  , - self.margin_to_line + self.b)
        y_margin_high = MinSlopePostProc.line(x_reg, self.res.x[0] , + self.margin_to_line + self.b)

        

        print(f'Distance in margin: {self.x_max_lin:.2f}')




        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter(x_in_margin, y_in_margin, color='green', label='Data Points in Margin' ) 
        plt.scatter(x_of_margin, y_of_margin, color='red', label='Data Points out of Margin' )
        plt.plot(x_reg, y_reg, color='red', label=f'Regression Line: m = {self.m:.2f}x b = {self.b} ')
        plt.axvline(self.x_max_lin, color='black', linestyle='--', label=f'Distance with lin behavior: {np.max(x_in_margin)}')
        plt.plot(x_reg, y_margin_low, color='green', linestyle='--', label=f'Lower Margin: m = {self.m:.2f}x b = {-self.margin_to_line} ')
        plt.plot(x_reg, y_margin_high, color='green', linestyle='--', label=f'Upper Margin: m = {self.m:.2f}x b = {+ self.margin_to_line} ')
        plt.axvline(0, color='black', linestyle='--')
        plt.xlabel('$H_{ex}$')
        plt.ylabel('$m_y$')
        plt.title(f'Iteration: {self.iter} Shape: {self.schape_name} Shape Info: {self.shape_info}')

        plt.legend()


        plt.show()
        plt.close()

    def save_postProc_plot(self, location, iter, full_path = True):

        if self.df is None:
            self.logger.error(f'[ERROR]: Trying to plot but No data loaded')
            raise ValueError(f'Skip Postprocessing')
        # Make sure the label has been calculated
        if self.res is None:
            self.calc_label()


        #x values 
        x_reg = np.linspace(self.df['H_ex'].min(), self.df['H_ex'].max(), 500)

        #calc number of points in the data wich are as close to calculated regression by threshhold
        #this is to see how well the regression fits the data

        #print(self.df['H_ex'])
        print(self.res.x[0])
        
        x_in_margin = self.df['H_ex'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) < self.margin_to_line]
        y_in_margin = self.df['M'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) < self.margin_to_line]
        x_of_margin = self.df['H_ex'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) >= self.margin_to_line]
        y_of_margin = self.df['M'][np.abs(self.df['M'] - MinSlopePostProc.line(self.df['H_ex'], self.res.x[0], self.b)) >= self.margin_to_line]

        y_reg = MinSlopePostProc.line(x_reg, self.res.x[0], self.b)
        y_margin_low = MinSlopePostProc.line(x_reg, self.res.x[0]  , - self.margin_to_line + self.b)
        y_margin_high = MinSlopePostProc.line(x_reg, self.res.x[0] , + self.margin_to_line + self.b)

        

        #print(f'Distance in margin: {self.x_max_lin:.2f}')




        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter(x_in_margin, y_in_margin, color='green', label='Data Points in Margin' ) 
        plt.scatter(x_of_margin, y_of_margin, color='red', label='Data Points out of Margin' )
        plt.plot(x_reg, y_reg, color='red', label=f'Regression Line: m = {self.m:.2f}x b = {self.b} ')
        plt.axvline(self.x_max_lin, color='black', linestyle='--', label=f'Distance with lin behavior: {np.max(x_in_margin)}')
        plt.plot(x_reg, y_margin_low, color='green', linestyle='--', label=f'Lower Margin: m = {self.m:.2f}x b = {-self.margin_to_line} ')
        plt.plot(x_reg, y_margin_high, color='green', linestyle='--', label=f'Upper Margin: m = {self.m:.2f}x b = {+ self.margin_to_line} ')
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

        try:
            plt.savefig(file_path)
        except:
            self.logger.warning(f"Could not save plot to {file_path}")
            
        plt.savefig(file_path)
        plt.close()
        self.logger.debug(f"Saved plot to {file_path}")

    








    
    def load_file(self, location: str, iter: int, micromag_ID: str, project_Name: str) -> pd.DataFrame:
        """Loads simulation data from a file into a DataFrame."""
        file_path = os.path.join(location, f"output/{iter}/microMag/slurm_{micromag_ID}/{project_Name}.dat")
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} does not exist")
            return pd.DataFrame()
        
        self.df = pd.read_csv(file_path, delim_whitespace=True, names=['time', 'H_ex', 'M'])
        return self.df
    
    def load_file_singe(self, file_path):
        """Loads simulation data from a file into a DataFrame."""
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} does not exist")
            return pd.DataFrame()
        
        self.df = pd.read_csv(file_path, delim_whitespace=True, names=['time', 'H_ex', 'M'])
        return self.df

    #2025-03-17 13:22:22,673 - MinSlopePostProc - ERROR - [Error]: File /ceph/home/fillies/tmr_sensors/thesis_versions/postproc_test/output/1/microMag/
    # slurm_<prerequisits.src.simulation.Simmulation object at 0x7d80fcbe6d70>/santa_tmp.dat does not exist

    def load_file(self, location: str, iter: int, micromag_ID: str, project_Name: str) -> pd.DataFrame:
    #def load_file(self, location,  iter, simulation, project_Name):
        #--------load file----------------
        

        file_path = os.path.join(location, f"output/{iter}/microMag/slurm_{micromag_ID}/{project_Name}.dat")
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
        return self.df

    
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
