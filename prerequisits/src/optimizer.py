from prerequisits.src.helper import *
from prerequisits.src.simulation import *
from prerequisits.src.Settings import *
from prerequisits.src.postProc import *
from prerequisits.src.database_handler import *
from prerequisits.src.configuration import *
from bayes_opt import BayesianOptimization, UtilityFunction

import copy
import logging

# SUpposed to perform the entiere optimzation

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
        self.read_only = True





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
        if self.optimizer is not None:
            self.logger.info("Reading Data from Database")
            self.load_data_from_database(self.database_handler)
        else:
            self.logger.error("trying to read data but no optimizer created yet to pass to")

        self.read_only = config.read_only
        if self.read_only:
            self.logger.info("Database opened in read-only mode no data will be saved. Which is not nice try to colaberate :/")
        
        # if the database is used also the first shape has to be loaded from the database
        self.logger.info("Overriding first shape from database")
        self.shape = self.get_initial_shape()


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
            

        

    def create_default_box(self):
        box = creat_default_box(location = self.location)
        self.logger.info("Default Box created")

        #adjust shape so that simulation will be over proper intervall
        box.hstart = 1
        box.hfinal = 0.0
        box.hstep = -0.5
        self.logger.info(f"Magenetig fieldrange set to hstart: {box.hstart}, hfinal: {box.hfinal}, hstep: {box.hstep}")

        #adjust mesh
            #mesh param
        box.main_Mesh_min = 0.1
        box.main_mesh_max = 1.0
        box.object_Mesh_max = 0.8
        self.logger.info(f"Mesh set to main_Meash_min: {box.main_Mesh_min}, main_mesh_max: {box.main_mesh_max}, object_Mesh_max: {box.object_Mesh_max}")

        self.shape = box
        self.logger.info(f"Box created with {box.get_info_shape()}")


    def creat_real_box(self, config: Config):
        """
        Create a real box with the given name.
        Not best practic but so far hardcode the specifics of the box in here.
        Olny saves the values to the bx does not apply any changes!!

        Args:
            name (str): The name of the box.

        Returns:
            None

        Raises:
            None
        """
        #self.logger.info("Creating real Box")

        box = creat_default_box(config)

        # adjust shape so that simulation will be over proper interval
        box.hstart = config.simulation.hstart
        box.hfinal = config.simulation.hfinal
        box.hstep = config.simulation.hstep
        self.logger.info(f"Magnetic field range set to hstart: {box.hstart}, hfinal: {box.hfinal}, hstep: {box.hstep}")

        # adjust mesh parameters
        box.main_Mesh_min = config.shape.main_Mesh_min
        box.main_mesh_max = config.shape.main_mesh_max
        box.object_Mesh_max = config.shape.object_Mesh_max
        self.logger.info(f"Mesh set to main_Mesh_min: {box.main_Mesh_min}, main_mesh_max: {box.main_mesh_max}, object_Mesh_max: {box.object_Mesh_max}")

        # adjust server settings
        box.number_cores = config.server.number_cores
        box.mem_GB = config.server.mem_GB
        self.logger.info(f"Server settings set to number_cores: {box.number_cores}, mem_GB: {box.mem_GB}")

        self.shape = box
        self.logger.info(f"Box created with {self.shape.get_info_shape()}")

    def bayesian_optimization_setup(self):
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
            pbounds = {'xlen': (1, 2), 'ylen': (0.1, 0.2), 'zlen': (0.01, 0.02)}

            

            # Initialize Bayesian Optimization without initial points
            self.optimizer = BayesianOptimization(
                f=None,  # Function is not directly used by the optimizer here
                pbounds=pbounds,
                random_state=42,
                verbose=2  # Verbose output (loggin level)
            )

            self.utility_bayesian = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)


    def update_database(self, param, label):
        """
        Update the database with the given parameters and label.

        Args:
            param (list): The parameters of the box.
            label (float): The label of the box.

        Returns:
            None
        """
        if self.database_handler is not None:
            number_inserted = self.database_handler.query_and_count(f"INSERT INTO shapes (xlen, ylen, zlen, linDis) VALUES ({param[0]}, {param[1]}, {param[2]}, {label})")
            self.logger.info(f"Updated {number_inserted} database with parameters: {param} and label: {label}")
        else:
            self.logger.debug("Database handler not initialized. Cannot update database.")

    


    def optimize(self):
        # check if box is created
        if self.shape is None:
            self.logger.error("No boshapex created yet")
            return
        
               
        if self.max_Iter is not None:
            self.logger.info(f"Starting optimization with {self.max_Iter} Iterations")
            
            for i in range(1, self.max_Iter + 1):
                self.iter = i
                self.logger.info(f"Starting Iteration {i}")
                self.current_simulation = Simmulation(self.shape,  self.location, iter=self.iter)
                self.current_simulation.run_Simulation()
                self.logger.debug("Starting post-processing")
                try:
                    postProc = self.post_process(i)
                    self.current_simulation.set_results(postProc.get_results())
                    self.all_simulations.append(copy.deepcopy(self.current_simulation))

                    params= self.shape.get_info_shape()
                    label = self.current_simulation.get_results().get_x_max_lin()
                    self.logger.info(f"Result of Post-Processing: lin Hysterese Distance: {label}")
                    
                    #save results globaly
                    if not self.read_only and self.database_handler is not None:
                        self.update_database(params, label)

                        # also save image of post process here
                        postProc.save_plot(self.database_handler.get_postProc_golbal_path(), params, full_path=False)

                    #save results localy
                    append_line_to_file(self.location + '/output/labels.txt', params, label)


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
        self.logger.debug(f"Init shape to: {new_suggestion}")
        new_shape = copy.deepcopy(self.shape)
        new_shape.set_xlen(new_suggestion['xlen'])
        new_shape.set_ylen(new_suggestion['ylen'])
        new_shape.set_zlen(new_suggestion['zlen'])

        return new_shape       

    def update_shape(self, params, label):
        """This function is used to finde the new shape of the box """
         # register old shape:
        self.optimizer.register(params, label)
        #get suggestion for new shape:
        new_suggestion = self.optimizer.suggest(self.utility_bayesian)
        self.logger.debug(f"New Suggestion for shape: {new_suggestion}")
        new_shape = copy.deepcopy(self.shape)
        new_shape.set_xlen(new_suggestion['xlen'])
        new_shape.set_ylen(new_suggestion['ylen'])
        new_shape.set_zlen(new_suggestion['zlen'])

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
        postProc.load_file(self.location,  self.iter, self.current_simulation, self.shape.get_project_name()) 
        self.logger.debug("File loaded")
        postProc.linear_regression()
        postProc.anasyse_data()
        postProc.save_plot(self.location, self.iter)
        return postProc
        
        

        
    



