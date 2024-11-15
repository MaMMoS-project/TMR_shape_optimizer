from prerequisits.src.helper import *
from prerequisits.src.simulation import *
from prerequisits.src.shape import *
from prerequisits.src.postProc import *
from prerequisits.src.database_handler import *
from prerequisits.src.configuration import *
from prerequisits.src.shape import *
from bayes_opt import BayesianOptimization, UtilityFunction

import math
import copy
import logging

# SUpposed to perform the entiere optimzationThis

class Optimizer:
    def __init__(self,locattion, max_Iter = None):
        # initialze logger
        """setup_logging(log_level, locattion )  # Assuming 3 is a high verbosity level equivalent to DEBUG
        logger = logging.getLogger(__name__)
        logger.debug("Logger Started")"""
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Logger Started")

        # set iter to zero at the begnning of optimization
        self.iter = 0

        # base location of main.py hast to be the same as prerequisits and is where results an operational_FIles will be created
        self.location = locattion
        self.logger.debug(f"Current Location set to {self.location}")

        # box is the object whis is simulated
        self.shape = None

        # set max Iterations is set to None it will run until other stop condition is met
        self.max_Iter = max_Iter

        # all Simulations
        self.current_simulation = None
        self.all_simulations = []

        # optimizer
        self.optimizer = None

        #database
        self.database_handler = None

        # True if results should not be updated into db
        self.read = True
        self.write = False






    def setup_database(self, config: DatabaseConfig):
        """
        Connect to the database.

        Args:
            db_path (str): The abs path to the database.

        Returns:
            None
        """
        self.database_handler = DatabaseHandler(config.db_path, config.postProc_global_path)
        self.logger.info(f"Connected to the database at {config.db_path}")
        self.logger.debug(f"Post-Processing results will be saved at {config.postProc_global_path}")

        #redd in data from database
        self.read = config.read
        self.write = config.write
        if self.read and self.write:
            self.logger.info("Database opened in read and write mode.")
        elif self.read:
            self.logger.info("Database opened in only in read mode.")
        elif self.write:
            self.logger.info("Database opened in only in write mode.")
        
        if self.optimizer is not None and self.read:
            self.logger.info("Reading Data from Database")
            self.load_data_from_database(self.database_handler)

        else:
            self.logger.error("trying to read data but no optimizer created yet to pass to")

        
        


    def load_data_from_database(self, database_handler):
        all_data = database_handler.query("SELECT * FROM shapes")
        # Initialize an empty list or dict to store successfully loaded data points
        successful_loads = []
        for data in all_data:
            try:
                # Assuming data[0], data[1], data[2] represent the parameters and data[3] the target
                self.optimizer.register([data[0], data[1], data[2]], data[3])
                successful_loads.append(data)
            except Exception as e:
                self.logger.warning(f"Could not load data from database for entry {data}: {str(e)}")
        
        # Check if any data was successfully loaded and update max accordingly
        if successful_loads:
            self.logger.info(f"{len(successful_loads)} data points successfully loaded from database.")
            # Assuming you have a method to compute 'max' from loaded data or it's computed during registration
            try:
                best_label = self.optimizer.max['target']
                self.logger.info(f"Best Label: {best_label}")
            except KeyError:
                self.logger.error("No 'target' found in optimizer max data. Check the optimizer's max computation logic.")
        else:
            self.logger.warning("No data points were successfully loaded from the database.")
            

        


    def bayesian_optimization_setup(self, config: Config):
            """
            Sets up the Bayesian Optimization for the optimizer.

            This method initializes the Bayesian Optimization with the specified parameter bounds and other settings.
            It also registers the default shape of the ox as the initial point for the optimizer.

            It also sets the bounds for the parameters to be optimized. This should be passed by main and not set here

            Parameters:
            - self: The instance of the optimizer class.

            Returns:
            - None
            """
            
            # for prove of concept use Bayes Optimizer
            # Bounded region of parameter space
            #pbounds = {'xlen': (5, 20), 'ylen': (0.1, 3), 'zlen': (0.005, 0.05)}
            if config.simulation.xlen_start > config.simulation.xlen_stop:
                logging.error("xlen_start has to be smaller than xlen_stop")
                exit()
            if config.simulation.ylen_start > config.simulation.ylen_stop:
                logging.error("ylen_start has to be smaller than ylen_stop")
                exit()
            if config.simulation.zlen_start > config.simulation.zlen_stop:
                logging.error("zlen_start has to be smaller than zlen_stop")
                exit()

            para_names = self.shape.param_names
            if len(para_names) == 0:
                logging.error("No parameter names found")
                exit()

            pbounds = {para_names[0]: (config.simulation.xlen_start, config.simulation.xlen_stop), para_names[1]: (config.simulation.ylen_start, config.simulation.ylen_stop), para_names[2]: (config.simulation.zlen_start, config.simulation.zlen_stop)}

            

            # Initialize Bayesian Optimization without initial points
            self.optimizer = BayesianOptimization(
                f=None,  # Function is not directly used by the optimizer here
                pbounds=pbounds,
                random_state=42,
                verbose=2  # Verbose output (loggin level)
            )
            

            self.utility_bayesian = UtilityFunction(kind=config.optimizer.acq_kind, kappa=config.optimizer.kappa, xi=config.optimizer.xi, kappa_decay=config.optimizer.kappa_decay, kappa_decay_delay=config.optimizer.kappa_decay_delay)
            self.logger.info(f"{self.utility_bayesian.kind} Utility function setup with kappa: {self.utility_bayesian.kappa}, xi: {self.utility_bayesian.xi}, kappa_decay: {self.utility_bayesian.kappa_decay}, kappa_decay_delay: {self.utility_bayesian.kappa_decay_delay}")
            self.logger.info(f"Bo setup with Acquisation function: {config.optimizer.acq_kind}, kappa: {config.optimizer.kappa}, xi: {config.optimizer.xi}, kappa_decay: {config.optimizer.kappa_decay}, kappa_decay_delay: {config.optimizer.kappa_decay_delay}")

    def update_database(self, param, label, eta=0.1):
        """
        Update the database with the given parameters and label.

        Args:
            param (list): The parameters of the box.
            label (float): The label of the box.

        Returns:
            None
        """
        if self.database_handler is not None:
            # Check if Data is in database
            data = self.database_handler.query(f"SELECT * FROM shapes WHERE xlen = {param[0]} AND ylen = {param[1]} AND zlen = {param[2]}")
            if data:
                self.logger.error(f"Data for parameters {data[0][3]} in database has different label {label}.")

            else:
                number_inserted = self.database_handler.query_and_count(f"INSERT INTO shapes (xlen, ylen, zlen, linDis) VALUES ({param[0]}, {param[1]}, {param[2]}, {label})")
                self.logger.info(f"Updated {number_inserted} database with parameters: {param} and label: {label}")
        else:
            self.logger.debug("Database handler not initialized. Cannot update database.")


    def creat_shape(self, config: Config):
        name = config.shape.name 
        if name == "Box":
            logging.info("Shape is Box")
            self.shape = Box(config)


        elif name == "Ellipse":
            logging.info("Shape is Ellipse")
            self.shape = Ellipse(config)
            
        
        elif name == "Stick":
            logging.info("Shape is Stick")
            self.shape = Stick(config)
            
        else:
            logging.error("Shape not recognized")
            exit()
    


    def optimize(self):
        # check if box is created
        if self.shape is None:
            self.logger.error("No shape created yet")
            return
        
               
        if self.max_Iter is not None:
            self.logger.info(f"Starting optimization with {self.max_Iter} Iterations")
            
            for i in range(1, self.max_Iter + 1):
                self.iter = i
                self.logger.info(f"Starting Iteration {i}")
                self.current_simulation = Simmulation(self.shape,  self.location, iter=self.iter)
                self.current_simulation.run_Simulation()        # does not return specific Data but saves the data to file where post process can access
                self.logger.debug("Starting post-processing")
                
                               
                
                try:
                    #perform post processing
                    postProc = self.post_process(i)
                    self.current_simulation.set_results(postProc.get_results())
                    self.all_simulations.append(copy.deepcopy(self.current_simulation))

                    #get results of post processing
                    params= self.shape.get_info_shape()
                    label = self.current_simulation.get_results().get_x_max_lin()
                    self.logger.info(f"Result of Post-Processing: lin Hysterese Distance: {label}")
                    
                    #save results globaly
                    if self.write and self.database_handler is not None:
                        self.update_database(params, label)

                        # also save image of post process here
                        
                        postProc.save_plot(self.database_handler.get_postProc_golbal_path(), params, full_path=False)


                    #save results localy
                    append_line_to_file(self.location + '/output/labels.txt', params, label)

                    #update shape
                    self.logger.debug("Updating shape")
                    self.shape = self.update_shape(params, label )
                    self.logger.info(f"Shape updated to {self.shape.get_info_shape()}")

                except Exception as e:
                    self.logger.error(f"Error during post-processing: {str(e)}")
                    self.logger.info("Disturbing the shape for next Iteration")
                    self.shape.disturbe_shape()
                    self.logger.info(f"Shape disturbed to {self.shape.get_info_shape()}")


    
                
    def get_initial_shape(self):
        new_suggestion = self.optimizer.suggest(self.utility_bayesian)
        self.logger.info(f"Init shape to: {new_suggestion}")
        new_shape = copy.deepcopy(self.shape)
        new_shape.update_shape(new_suggestion)

        return new_shape       

    def update_shape(self, params, label):
         # register old shape:
        self.optimizer.register(params, label)
        #get suggestion for new shape:
        new_suggestion = self.optimizer.suggest(self.utility_bayesian)
        self.logger.debug(f"New Suggestion for shape: {new_suggestion}")
        new_shape = copy.deepcopy(self.shape)
        new_shape.update_shape(new_suggestion)

        return new_shape

    def post_process(self, iter, threshhold_training=0.5, margin_to_line=0.05, m_guess=3):
        """
        Perform post-processing on the data.

        Args:
            threshhold_training (float): starting from 0 on how much data will be used for training the linear 
                                        regression of middel part of hysteresis loop
                                        if choosen too high hysteresis loop wont have linear behaviour
            margin_to_line (float): margin to line is the distance between the regression line and the data points with linear behaviour
            m_guess (int): initial guess for the slope of the regression line does not real matter

        Returns:
            dict: The post-processing results.
        """
        
        postProc = PostProc(threshhold_training, margin_to_line, m_guess, self.shape, iter)
        #load .dat file
        postProc.load_file(self.location,  self.iter, self.current_simulation, self.shape.get_project_name()) 
        self.logger.debug("File loaded")
        #perform linear regression
        postProc.linear_regression(regression_restart_counter = 0)
        self.logger.debug("Linear Regression done")
        # anlayse data towards the linear regression
        postProc.anasyse_data()
    
        postProc.save_plot(self.location, self.iter)
        return postProc
        
        

        
    



