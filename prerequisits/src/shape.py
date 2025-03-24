import numpy as np
import os
from prerequisits.src.configuration import *
import logging
import sys
from abc import ABC, abstractmethod

class Shape:
    # Assuming some basic implementation or properties for SimulationSettings
    def __init__(self, config: Config):
        """
        Never to be initialized directly. Contains the cofigureation which are the same for every Shae (Boc esslipy,....) of the object to be simulated.
        If config is modifexy add here
        """
        # Initialize some common simulation settings
        self.projectName = config.simulation.sim_name
        self.logger = logging.getLogger(__name__)
        self.param_names= []

        #air box scaliing factors
        self.smallBox_factor = 3  #>0
        self.bigBox_factor = 11   #>smallBox_factor
        
        
        #mesh param
        self.main_Mesh_min = config.simulation.main_Mesh_min
        self.main_mesh_max = config.simulation.main_mesh_max
        self.object_Mesh_max = config.simulation.object_Mesh_max

        self.testGeomatrySettings()
        logging.info(f"Mesh setting: main_Mesh_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}")
        
        # path to templated
        self.p2_file_path = os.path.join(config.generalSettings.location, "prerequisits/_template_.p2")
        self.element_specs_path = os.path.join(config.generalSettings.location,"prerequisits/_template_.krn")
        self.slurm_path = os.path.join(config.generalSettings.location,"prerequisits/_template_.slurm")
        self.slurm_salome_path = os.path.join(config.generalSettings.location,"prerequisits/salome.slurm")

        #[initial state]
        self.mx = 1.
        self.my = 0.
        self.mz = 0.
        #[field]
        self.hstart = config.simulation.hstart          
        self.hfinal = config.simulation.hfinal
        self.hstep = config.simulation.hstep
        self.mfinal = -0.5
        self.mstep = 0.5
        self.hx = 0.034
        self.hy = 1.0
        self.hz = 0.0

        self.test_Sim_settings()
        logging.info(f"H-Fieln settings: hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}")
        
        #[minimizer] 
        self.tol_fun = 1.0e-10
        self.cg_method = 1004
        self.precond_iter = 10
        self.hmag_on = 1
        self.print_hmag = 0
        self.verbose = 0

        self.number_cores = config.server.number_cores
        self.mem_GB = config.server.mem_GB
        self.gpu = config.server.gpu
        logging.info (f"Server settings: number_cores={self.number_cores}, mem_GB={self.mem_GB}, gpu={self.gpu}")


    

        logging.debug(f"general Shape initialized")

    @abstractmethod
    def update_shape(self, param):
        'enables the updated shape to be set'
        pass

    @abstractmethod
    def testSpecificSape(self):
        pass

    @abstractmethod
    def modify_specific_shape_setting(self, location):
        pass

    @abstractmethod
    def disturbe_shape(self, percent):
        pass

    @abstractmethod
    def print_shape_info(self):
        pass 

    @abstractmethod
    def print_shape_info_short(self):
        pass

    @abstractmethod
    def get_info_shape(self):
        pass
    
    @abstractmethod
    def get_info_shape(self):
        pass

    @abstractmethod
    def save_box_info_to_file(self, current_dir):
        pass


    def testGeomatrySettings(self):
        # test if small box smaller as bigBox:
        if self.smallBox_factor >= self.bigBox_factor:
            logging.error("Small box needs to be smaller than big box")
            sys.exit()
        
        # test if small box smaller as bigBox:
        if self.main_Mesh_min >= self.main_mesh_max:
            logging.error("main_Mesh_min needs to be smaller than main_mesh_max")
            sys.exit()
        # test if small box smaller as bigBox:
        if self.main_mesh_max <= self.object_Mesh_max:
            logging.error("main_mesh_max needs to be bigger than object_Mesh_max")
            sys.exit()
        # check if every value is biggen than 0
        variables = [self.smallBox_factor, 
                     self.bigBox_factor, self.main_Mesh_min, 
                     self.main_mesh_max, self.object_Mesh_max]
        # Check if all variables are greater than 0
        # Convert all variables to floats and check if any are less than or 
        # equal to 0
        if any(float(var) <= 0 for var in variables):
            logging.error("All variables must be greater than 0")
            sys.exit()

    def test_Sim_settings(self):
        if np.abs(self.hfinal - self.hstart) < self.hstep:
            logging.error("hfinal - hstart needs to be bigger than hstep")
            sys.exit()

    def apply_all_modifications(self, current_script_dir):
        self.modify_element_specs(current_script_dir)
        self.modify_specific_shape_setting(current_script_dir)
        self.modify_sim_slurm(current_script_dir)
        self.modify_sim_settings(current_script_dir)
        self.modify_salome_slurm(current_script_dir)

    def modify_element_specs(self, current_script_dir):
        """
        Modifies the element specifications file for simulation.

        Args:
            current_script_dir (str): The directory containing the current element specs script.
        """
        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.element_specs_path)
        file_path_modifies = os.path.join(current_script_dir, "operations_Files/" + str(self.projectName) + ".krn")

        self.logger.debug(f"Modifying element specs script at '{file_path}'.")
        
        # Read the original script content
        try:
            with open(file_path, 'r') as file:
                script_content = file.read()
                self.logger.debug("Successfully read the original element specs script.")
        except FileNotFoundError:
            self.logger.error(f"Element specs file '{file_path}' does not exist.")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An error occurred while reading '{file_path}': {e}")
            sys.exit(1)

        # Here we could add modification logic if needed (similar to modify_sim_slurm)
        # Currently, just copying the content without modifications
        
        # Write the modified script content back to a new file
        try:
            with open(file_path_modifies, 'w') as file:
                file.write(script_content)
                self.logger.debug(f"Successfully wrote the modified element specs script to '{file_path_modifies}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to '{file_path_modifies}': {e}")
            sys.exit(1)

    def modify_sim_slurm(self, current_script_dir):
        """
        Modifies the SLURM script for simulation.

        Args:
            current_script_dir (str): The directory containing the current SLURM script.
        """
        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.slurm_path)
        file_path_modifies = os.path.join(current_script_dir, "operations_Files/" + str(self.projectName) + ".slurm")

        self.logger.debug(f"Modifying SLURM script at '{file_path}'.")
        
        # Read the original script content
        with open(file_path, 'r') as file:
            script_content = file.read()

        # Modify the script content
        modifications = {
            'MODELNAME="<model>"': f'MODELNAME="{self.projectName}"',
            '<description>': str(self.projectName),
            '--mem-per-gpu=15': f'--mem-per-cpu={self.mem_GB}',
            #'--cpus-per-task=1': f'--cpus-per-task={self.number_cores}',
            '--constraint=nv12': f'--constraint={self.gpu}'
        }
        
        for key, value in modifications.items():
            if key in script_content:
                script_content = script_content.replace(key, value)
                self.logger.debug(f"Replaced '{key}' with '{value}' in SLURM script.")
            else:
                self.logger.warning(f"Key '{key}' not found in SLURM script. No replacement made.")

        # Write the modified script content back to a new file
        try:
            with open(file_path_modifies, 'w') as file:
                file.write(script_content)
                self.logger.debug(f"Successfully wrote the modified SLURM script to '{file_path_modifies}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to '{file_path_modifies}': {e}")
            sys.exit(1)
    
    def modify_sim_settings(self, current_script_dir):
        """
        Modifies the simulation settings for the script.

        Args:
            current_script_dir (str): The directory containing the current simulation settings script.
        """
        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.p2_file_path)
        file_path_modifies = os.path.join(current_script_dir, "operations_Files/" + str(self.projectName) + ".p2")

        self.logger.debug(f"Modifying simulation settings at '{file_path}'.")
        
        # Read the original script content
        with open(file_path, 'r') as file:
            script_content = file.read()

        # Modify the script content
        modifications = {
            'mx = 1.': f'mx = {self.mx}',
            'my = 0.': f'my = {self.my}',
            'mz = 0.': f'mz = {self.mz}',
            'hstart = 1.5': f'hstart = {self.hstart}',
            'hfinal = -8.0': f'hfinal = {self.hfinal}',
            'hstep = -0.001': f'hstep = {self.hstep}',
            'mfinal = -0.5': f'mfinal = {self.mfinal}',
            'mstep = 0.5': f'mstep = {self.mstep}',
            'hx = 0.0': f'hx = {self.hx}',
            'hy = 0.034': f'hy = {self.hy}',
            'hz = 1.': f'hz = {self.hz}',
            'tol_fun = 1.0e-10': f'tol_fun = {self.tol_fun}',
            'cg_method = 1004': f'cg_method = {self.cg_method}',
            'precond_iter = 10': f'precond_iter = {self.precond_iter}',
            'hmag_on = 1': f'hmag_on = {self.hmag_on}',
            'print_hmag = 0': f'print_hmag = {self.print_hmag}',
            'verbose = 0': f'verbose = {self.verbose}'
        }
        
        for key, value in modifications.items():
            if key in script_content:
                script_content = script_content.replace(key, value)
                self.logger.debug(f"Replaced '{key}' with '{value}' in simulation settings script.")
            else:
                self.logger.warning(f"Key '{key}' not found in simulation settings script. No replacement made.")

        # Write the modified script content back to a new file
        try:
            with open(file_path_modifies, 'w') as file:
                file.write(script_content)
                self.logger.debug(f"Successfully wrote the modified simulation settings script to '{file_path_modifies}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to '{file_path_modifies}': {e}")
            sys.exit(1)

    def modify_salome_slurm(self, current_script_dir):
        """
        Modifies the SLURM script used specifically for Salome mesh generation.

        Args:
            current_script_dir (str): The directory containing the current SLURM script for Salome.
        """
        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.slurm_salome_path)
        file_path_modifies = os.path.join(current_script_dir, "operations_Files/salome.slurm")

        self.logger.debug(f"Modifying Salome SLURM script at '{file_path}'.")
        
        # Read the original script content
        try:
            with open(file_path, 'r') as file:
                script_content = file.read()
                self.logger.debug("Successfully read the original Salome SLURM script.")
        except FileNotFoundError:
            self.logger.error(f"Salome SLURM script file '{file_path}' does not exist.")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An error occurred while reading '{file_path}': {e}")
            sys.exit(1)

        # Modify the script content
        modifications = {
            '--job-name="<description>"': f'--job-name="{self.projectName}"',
            '--mem-per-cpu=25': f'--mem-per-cpu={self.mem_GB}',
            '--cpus-per-task=2': f'--cpus-per-task={self.number_cores}',
            '"$SLURM_SUBMIT_DIR"/step2_salome_macroFullLM_2nm.py': '"$SLURM_SUBMIT_DIR"/salome_mesh.py',
            'step2_salome_macroFullLM_2nm.py': 'salome_mesh.py'
        }
        
        for key, value in modifications.items():
            if key in script_content:
                script_content = script_content.replace(key, value)
                self.logger.debug(f"Replaced '{key}' with '{value}' in Salome SLURM script.")
            else:
                self.logger.warning(f"Key '{key}' not found in Salome SLURM script. No replacement made.")

        # Write the modified script content back to a new file
        try:
            with open(file_path_modifies, 'w') as file:
                file.write(script_content)
                self.logger.debug(f"Successfully wrote the modified Salome SLURM script to '{file_path_modifies}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to '{file_path_modifies}': {e}")
            sys.exit(1)

    def get_project_name(self):
        return self.projectName
    

    
class Ellipse(Shape):
    def __init__(self, config: Config):
        super().__init__(config)
        
        self.modifyer_path = os.path.join(config.generalSettings.location, "prerequisits/src/ellipse_creator.py")
        self.param_names = ["xlen", "ylen", "zlen"]
        #target box size (this is the magnet)
        self.xlen = config.shape.init_xlen
        self.ylen = config.shape.init_ylen
        self.zlen = config.shape.init_zlen

        self.testSpecificSape()
        logging.info(f"Ellipse Shape initialized with shape [{self.xlen}, {self.ylen}, {self.zlen}], and shallow input Tests")


    def update_shape(self, param):
        if len(param) != 3:
            logging.error("Ellipse needs to have 3 values (x,y,z)")
            sys.exit()
        self.xlen = param['xlen']
        self.ylen = param['ylen']
        self.zlen = param['zlen']


    def testSpecificSape(self):
        if self.xlen < 0:
            logging.error("xlen needs to be bigger than 0")
            sys.exit()
        if self.ylen < 0:
            logging.error("ylen needs to be bigger than 0")
            sys.exit()
        if self.zlen < 0:
            logging.error("ylen needs to be bigger than 0")
            sys.exit()


    def modify_specific_shape_setting(self, location):
        """
        Modifies the geometry settings script.

        Args:
            location (str): The directory containing the geometry settings script.
        """
        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(location, self.modifyer_path)
        file_path_modifies = os.path.join(location, "operations_Files/salome_mesh.py")

        self.logger.debug(f"Modifying geometry settings at '{file_path}'.")
        
        # Read the original script content
        try:
            with open(file_path, 'r') as file:
                script_content = file.read()
                self.logger.debug("Successfully read the original geometry settings script.")
        except FileNotFoundError:
            self.logger.error(f"Geometry settings file '{file_path}' does not exist.")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An error occurred while reading '{file_path}': {e}")
            sys.exit(1)

        # Modify the script content
        modifications = {
            '/ceph/home/fillies/tmr_sensor_sensors/automatization': str(location),
            'xlen = 1': f'xlen = {self.xlen}',
            'ylen = 0.1': f'ylen = {self.ylen}',
            'zlen = 0.01': f'zlen = {self.zlen}',
            'smallBox_factor = 3': f'smallBox_factor = {self.smallBox_factor}',
            'bigBox_factor = 11': f'bigBox_factor = {self.bigBox_factor}',
            'main_Meash_min = 0.00001': f'main_Meash_min = {self.main_Mesh_min}',
            'main_mesh_max = 1': f'main_mesh_max = {self.main_mesh_max}',
            'object_Mesh_max = 0.005': f'object_Mesh_max = {self.object_Mesh_max}'
        }
        
        for key, value in modifications.items():
            if key in script_content:
                script_content = script_content.replace(key, value)
                self.logger.debug(f"Replaced '{key}' with '{value}' in geometry settings script.")
            else:
                self.logger.warning(f"Key '{key}' not found in geometry settings script. No replacement made.")

        # Write the modified script content back to a new file
        try:
            with open(file_path_modifies, 'w') as file:
                file.write(script_content)
                self.logger.debug(f"Successfully wrote the modified geometry settings script to '{file_path_modifies}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to '{file_path_modifies}': {e}")
            sys.exit(1)
    
        
    def disturbe_shape(self, percent=5):
        #randmly add or subracts up to 5 % of value
        self.xlen = self.xlen + self.xlen * np.random.uniform(-percent/100, percent/100)
        self.ylen = self.ylen + self.ylen * np.random.uniform(-percent/100, percent/100)
        self.zlen = self.zlen + self.zlen * np.random.uniform(-percent/100, percent/100)

    def print_shape_info(self):
        print(f"Project Name: {self.projectName}")
        print(f"Ellipse Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}")
        print(f"Small Box Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}")
        print(f"Mesh Settings: main_Meash_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}")
        print(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}")
        print(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}")
        print(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}") 


    def print_shape_info_short(self):
        print(f"Project Name: {self.projectName}")
        print(f"Ellipse Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}")
        print(f"Small Box Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}")
        print(f"Mesh Settings: main_Meash_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}")
        print(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}")
        print(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}")
        print(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}")


    def get_info_shape(self):
        return [self.xlen, self.ylen, self.zlen]
    

    def save_box_info_to_file(self, current_dir):
        file_path = os.path.join(current_dir, "operations_Files/" + str(self.projectName) + ".txt")
        with open(file_path, 'w') as file:
            file.write(f"Project Name: {self.projectName}\n")
            file.write(f"Ellipse Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}\n")
            file.write(f"Small Box Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}\n")
            file.write(f"Mesh Settings: main_Meash_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}\n")
            file.write(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}\n")
            file.write(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}\n")
            file.write(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}\n")
        logging.info(f"Saved Ellipse info to file '{file_path}'.")







class Box(Shape):
    def __init__(self, config: Config):
        super().__init__(config)
        
        self.modifyer_path = os.path.join(config.generalSettings.location, "prerequisits/src/box_creator.py")
        self.param_names = ["xlen", "ylen", "zlen"]
        #target box size (this is the magnet)
        self.xlen = config.shape.init_xlen
        self.ylen = config.shape.init_ylen
        self.zlen = config.shape.init_zlen
                
        self.testSpecificSape()
        logging.info(f"Box Shape initialized with shape [{self.xlen}, {self.ylen}, {self.zlen}], and shallow input Tests")

    def disturbe_shape(self, percent=5):
        #randmly add or subracts up to 5 % of value
        self.xlen = self.xlen + self.xlen * np.random.uniform(-percent/100, percent/100)
        self.ylen = self.ylen + self.ylen * np.random.uniform(-percent/100, percent/100)
        self.zlen = self.zlen + self.zlen * np.random.uniform(-percent/100, percent/100)

    def update_shape(self, param):
        if len(param) != 3:
            logging.error("Box needs to have 3 values (x,y,z)")
            sys.exit()
        self.xlen = param['xlen']
        self.ylen = param['ylen']
        self.zlen = param['zlen']


    def testSpecificSape(self):
        if self.xlen < 0:
            logging.error("xlen needs to be bigger than 0")
            sys.exit()
        if self.ylen < 0:
            logging.error("ylen needs to be bigger than 0")
            sys.exit()
        if self.zlen < 0:
            logging.error("ylen needs to be bigger than 0")
            sys.exit()

    def modify_specific_shape_setting(self, location):
        """
        Modifies the geometry settings script.

        Args:
            location (str): The directory containing the geometry settings script.
        """
        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(location, self.modifyer_path)
        file_path_modifies = os.path.join(location, "operations_Files/salome_mesh.py")

        self.logger.debug(f"Modifying geometry settings at '{file_path}'.")
        
        # Read the original script content
        try:
            with open(file_path, 'r') as file:
                script_content = file.read()
                self.logger.debug("Successfully read the original geometry settings script.")
        except FileNotFoundError:
            self.logger.error(f"Geometry settings file '{file_path}' does not exist.")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An error occurred while reading '{file_path}': {e}")
            sys.exit(1)

        # Modify the script content
        modifications = {
            '/ceph/home/fillies/tmr_sensor_sensors/automatization': str(location),
            'xlen = 1': f'xlen = {self.xlen}',
            'ylen = 0.1': f'ylen = {self.ylen}',
            'zlen = 0.01': f'zlen = {self.zlen}',
            'smallBox_factor = 3': f'smallBox_factor = {self.smallBox_factor}',
            'bigBox_factor = 11': f'bigBox_factor = {self.bigBox_factor}',
            'main_Meash_min = 0.00001': f'main_Meash_min = {self.main_Mesh_min}',
            'main_mesh_max = 1': f'main_mesh_max = {self.main_mesh_max}',
            'object_Mesh_max = 0.005': f'object_Mesh_max = {self.object_Mesh_max}'
        }
        
        for key, value in modifications.items():
            if key in script_content:
                script_content = script_content.replace(key, value)
                self.logger.debug(f"Replaced '{key}' with '{value}' in geometry settings script.")
            else:
                self.logger.warning(f"Key '{key}' not found in geometry settings script. No replacement made.")

        # Write the modified script content back to a new file
        try:
            with open(file_path_modifies, 'w') as file:
                file.write(script_content)
                self.logger.debug(f"Successfully wrote the modified geometry settings script to '{file_path_modifies}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to '{file_path_modifies}': {e}")
            sys.exit(1)
    
        
    def print_shape_info(self):
        print(f"Project Name: {self.projectName}")
        print(f"Box Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}")
        print(f"Small Box Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}")
        print(f"Mesh Settings: main_Mesh_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}")
        print(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}")
        print(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}")
        print(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}")
        print(f"File Paths: p2_file_path={self.p2_file_path}, modifyer_path={self.modifyer_path}, element_specs_path={self.element_specs_path}")
        print(f"Slurm Paths: sim_slurm_path={self.slurm_path}, salome_slurm_path={self.slurm_salome_path}")

    def print_shape_info_short(self):
        print(f"Project Name: {self.projectName}")
        print(f"Box Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}")

    def get_info_shape(self):
        return [self.xlen, self.ylen, self.zlen]
 
    def save_box_info_to_file(self, current_dir):
        # Construct the file path for 'shape_info.txt' in the current directory
        file_path = os.path.join(current_dir, 'shape_info.txt')

        with open(file_path, 'w') as file:
            file.write(f"Project Name: {self.projectName}\n")
            # Add other information as in the previous example...
            file.write(f"Project Name: {self.projectName}\n")
            file.write(f"Box Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}\n")
            file.write(f"Small Box Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}\n")
            file.write(f"Mesh Settings: main_Mesh_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}\n")
            file.write(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}\n")
            file.write(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}\n")
            file.write(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}\n")
            file.write(f"File Paths: p2_file_path={self.p2_file_path}, modifyer_path={self.modifyer_path}, element_specs_path={self.element_specs_path}\n")
            file.write(f"Slurm Paths: sim_slurm_path={self.slurm_path}, salome_slurm_path={self.slurm_salome_path}\n")
            
        print(f"Box information saved to '{file_path}'")






class Stick(Shape):
    def __init__(self, config: Config):
        super().__init__(config)
        
        self.modifyer_path = os.path.join(config.generalSettings.location, "prerequisits/src/stick_creator.py")
        self.param_names = ["xlen", "ylen", "zlen"]
        #target stick size (this is the magnet)
        self.xlen = config.shape.init_xlen
        self.ylen = config.shape.init_ylen
        self.zlen = config.shape.init_zlen
                
        self.testSpecificSape()
        logging.info(f"Stick Shape initialized with shape [{self.xlen}, {self.ylen}, {self.zlen}], and shallow input Tests")

    def disturbe_shape(self, percent=5):
        #randmly add or subracts up to 5 % of value
        self.xlen = self.xlen + self.xlen * np.random.uniform(-percent/100, percent/100)
        self.ylen = self.ylen + self.ylen * np.random.uniform(-percent/100, percent/100)
        self.zlen = self.zlen + self.zlen * np.random.uniform(-percent/100, percent/100)

    def update_shape(self, param):
        if len(param) != 3:
            logging.error("Stick needs to have 3 values (x,y,z)")
            sys.exit()
        self.xlen = param['xlen']
        self.ylen = param['ylen']
        self.zlen = param['zlen']


    def testSpecificSape(self):
        if self.xlen < 0:
            logging.error("xlen needs to be bigger than 0")
            sys.exit()
        if self.ylen < 0:
            logging.error("ylen needs to be bigger than 0")
            sys.exit()
        if self.zlen < 0:
            logging.error("ylen needs to be bigger than 0")
            sys.exit()

    def modify_specific_shape_setting(self, location):
        """
        Modifies the geometry settings script.

        Args:
            location (str): The directory containing the geometry settings script.
        """
        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(location, self.modifyer_path)
        file_path_modifies = os.path.join(location, "operations_Files/salome_mesh.py")

        self.logger.debug(f"Modifying geometry settings at '{file_path}'.")
        
        # Read the original script content
        try:
            with open(file_path, 'r') as file:
                script_content = file.read()
                self.logger.debug("Successfully read the original geometry settings script.")
        except FileNotFoundError:
            self.logger.error(f"Geometry settings file '{file_path}' does not exist.")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"An error occurred while reading '{file_path}': {e}")
            sys.exit(1)

        # Modify the script content
        modifications = {
            '/ceph/home/fillies/tmr_sensor_sensors/automatization': str(location),
            'xlen = 1': f'xlen = {self.xlen}',
            'ylen = 0.1': f'ylen = {self.ylen}',
            'zlen = 0.01': f'zlen = {self.zlen}',
            'smallBox_factor = 3': f'smallBox_factor = {self.smallBox_factor}',
            'bigBox_factor = 11': f'bigBox_factor = {self.bigBox_factor}',
            'main_Meash_min = 0.00001': f'main_Meash_min = {self.main_Mesh_min}',
            'main_mesh_max = 1': f'main_mesh_max = {self.main_mesh_max}',
            'object_Mesh_max = 0.005': f'object_Mesh_max = {self.object_Mesh_max}'
        }
        
        for key, value in modifications.items():
            if key in script_content:
                script_content = script_content.replace(key, value)
                self.logger.debug(f"Replaced '{key}' with '{value}' in geometry settings script.")
            else:
                self.logger.warning(f"Key '{key}' not found in geometry settings script. No replacement made.")

        # Write the modified script content back to a new file
        try:
            with open(file_path_modifies, 'w') as file:
                file.write(script_content)
                self.logger.debug(f"Successfully wrote the modified geometry settings script to '{file_path_modifies}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to '{file_path_modifies}': {e}")
            sys.exit(1)
    
        
    def print_shape_info(self):
        print(f"Project Name: {self.projectName}")
        print(f"stick Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}")
        print(f"Small Box Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}")
        print(f"Mesh Settings: main_Mesh_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}")
        print(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}")
        print(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}")
        print(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}")
        print(f"File Paths: p2_file_path={self.p2_file_path}, modifyer_path={self.modifyer_path}, element_specs_path={self.element_specs_path}")
        print(f"Slurm Paths: sim_slurm_path={self.slurm_path}, salome_slurm_path={self.slurm_salome_path}")

    def print_shape_info_short(self):
        print(f"Project Name: {self.projectName}")
        print(f"stick Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}")

    def get_info_shape(self):
        return [self.xlen, self.ylen, self.zlen]
 
    def save_stick_info_to_file(self, current_dir):
        # Construct the file path for 'shape_info.txt' in the current directory
        file_path = os.path.join(current_dir, 'shape_info.txt')

        with open(file_path, 'w') as file:
            file.write(f"Project Name: {self.projectName}\n")
            # Add other information as in the previous example...
            file.write(f"Project Name: {self.projectName}\n")
            file.write(f"stick Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}\n")
            file.write(f"Small stick Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}\n")
            file.write(f"Mesh Settings: main_Mesh_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}\n")
            file.write(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}\n")
            file.write(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}\n")
            file.write(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}\n")
            file.write(f"File Paths: p2_file_path={self.p2_file_path}, modifyer_path={self.modifyer_path}, element_specs_path={self.element_specs_path}\n")
            file.write(f"Slurm Paths: sim_slurm_path={self.slurm_path}, salome_slurm_path={self.slurm_salome_path}\n")
            
        print(f"stick information saved to '{file_path}'")








 








    





    






