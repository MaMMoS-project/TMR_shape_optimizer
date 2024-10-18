import numpy as np
import os
from prerequisits.src.configuration import *
import logging
import sys

class SimulationSettings:
    # Assuming some basic implementation or properties for SimulationSettings
    def __init__(self, projectName):
        # Initialize some common simulation settings
        self.projectName = projectName
        self.logger = logging.getLogger(__name__)


class Box(SimulationSettings):
    def __init__(self, projectName):
        super().__init__(projectName)  # Initialize the parent class

        
    def testGeomatrySettings(self):
        # test if small box smaller as bigBox:
        if self.smallBox_factor >= self.bigBox_factor:
            raise ValueError("smallBox need to be smaller than bigbox")
        
        # test if small box smaller as bigBox:
        if self.main_Mesh_min >= self.main_mesh_max:
            raise ValueError("Max mesh needs to be bigger than min Mesh")
        # test if small box smaller as bigBox:
        if self.main_mesh_max <= self.object_Mesh_max:
            raise ValueError("Object Mesh should be smaller than maxMesh")
        
        # check if every value is biggen than 0
        variables = [self.xlen, self.ylen, self.zlen, self.smallBox_factor, 
                     self.bigBox_factor, self.main_Mesh_min, 
                     self.main_mesh_max, self.object_Mesh_max]
        # Check if all variables are greater than 0
        # Convert all variables to floats and check if any are less than or 
        # equal to 0
        if any(float(var) <= 0 for var in variables):
            raise ValueError("All values need to be positive")

    def test_Sim_settings(self):
        if np.abs(self.hfinal - self.hstart) < self.hstep:
            raise ValueError("hrange not propperly defined")

    def set_smallBox_factor(self, smallBox_factor):
        self.smallBox_factor = smallBox_factor

    def set_bigBox_factor(self, bigBox_factor):
        self.bigBox_factor = bigBox_factor

    def set_main_Mesh_min(self, main_Mesh_min):
        self.main_Mesh_min = main_Mesh_min

    def set_main_mesh_max(self, main_mesh_max):
        self.main_mesh_max = main_mesh_max

    def set_object_Mesh_max(self, object_Mesh_max):
        self.object_Mesh_max = object_Mesh_max

    def set_box_modifyer_path(self, box_modifyer_path):
        self.box_modifyer_path = box_modifyer_path

    def set_element_specs_path(self, element_specs_path):
        self.element_specs_path = element_specs_path

    def set_slurm_path(self, slurm_path):
        self.slurm_path = slurm_path

    def set_slurm_salome_path(self, slurm_salome_path):
        self.slurm_salome_path = slurm_salome_path

    def set_sim_settings(self, mx, my, mz, hstart, hfinal, hstep, mfinal, 
                         mstep, hx, hy, hz, tol_fun, cg_method,
                         precond_iter, hmag_on, print_hmag, verbose,
                         p2_file_path):
        self.mx = mx
        self.my = my
        self.mz = mz
        self.hstart = hstart
        self.hfinal = hfinal
        self.hstep = hstep
        self.mfinal = mfinal
        self.mstep = mstep
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.tol_fun = tol_fun
        self.cg_method = cg_method
        self.precond_iter = precond_iter
        self.hmag_on = hmag_on
        self.print_hmag = print_hmag
        self.verbose = verbose
        self.p2_file_path = p2_file_path

    def modify_sim_settings(self, current_script_dir):

        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.p2_file_path)

        file_path_modifies = os.path.join(current_script_dir,
                                          "operations_Files/" +
                                          str(self.projectName) +
                                          ".p2")

        # Read the original script content
        with open(file_path, 'r') as file:
            script_content = file.read()

        # Modify the script content
        script_content = script_content.replace('mx = 0.', 'mx = ' + 
                                                str(self.mx))
        script_content = script_content.replace('my = 0.', 'my = ' + 
                                                str(self.my))
        script_content = script_content.replace('mz = 1.', 'mz = ' + 
                                                str(self.mz))
        script_content = script_content.replace('hstart = 1.5', 'hstart = ' +
                                                str(self.hstart))
        script_content = script_content.replace('hfinal = -8.0', 'hfinal = ' +
                                                str(self.hfinal))
        script_content = script_content.replace('hstep = -0.001', 'hstep = ' +
                                                str(self.hstep))
        script_content = script_content.replace('mfinal = -0.5', 'mfinal = ' +
                                                str(self.mfinal))
        script_content = script_content.replace('mstep = 0.5', 'mstep = ' +
                                                str(self.mstep))
        script_content = script_content.replace('hx = 0.0', 'hx = ' +
                                                str(self.hx))
        script_content = script_content.replace('hy = 0.034', 'hy = ' +
                                                str(self.hy))
        script_content = script_content.replace('hz = 1.', 'hz = ' +
                                                str(self.hz))
        script_content = script_content.replace('tol_fun = 1.0e-10',
                                                'tol_fun = ' +
                                                str(self.tol_fun))
        script_content = script_content.replace('cg_method = 1004',
                                                'cg_method = ' +
                                                str(self.cg_method))
        script_content = script_content.replace('precond_iter = 10',
                                                'precond_iter = ' +
                                                str(self.precond_iter))
        script_content = script_content.replace('hmag_on = 1', 'hmag_on = ' +
                                                str(self.hmag_on))
        script_content = script_content.replace('print_hmag = 0',
                                                'print_hmag = ' +
                                                str(self.print_hmag))
        script_content = script_content.replace('verbose = 0', 'verbose = '
                                                + str(self.verbose))
        
        # Write the modified script content back to the same file
        with open(file_path_modifies, 'w') as file:
            file.write(script_content)

    def setGeometrySettings(self, xlen, ylen, zlen, smallBox_factor,
                            bigBox_factor, main_Mesh_min, main_mesh_max,
                            object_Mesh_max, box_modifyer_path):
        self.xlen = xlen
        self.ylen = ylen
        self.zlen = zlen
        self.smallBox_factor = smallBox_factor
        self.bigBox_factor = bigBox_factor
        self.main_Mesh_min = main_Mesh_min
        self.main_mesh_max = main_mesh_max
        self.object_Mesh_max = object_Mesh_max
        self.box_modifyer_path = box_modifyer_path

    def modify_geo_settings(self, location):
        

        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(location, self.box_modifyer_path)

        file_path_modifies = os.path.join(location,
                                          "operations_Files/salome_mesh.py")

        # Read the original script content
        with open(file_path, 'r') as file:
            script_content = file.read()

        # Modify the script 
        script_content = script_content.replace('/ceph/home/fillies/tmr_sensor_sensors/automatization', 
                                                str(location))
        script_content = script_content.replace('xlen = 1', 'xlen = ' + 
                                                str(self.xlen))
        script_content = script_content.replace('ylen = 0.1', 'ylen = ' + 
                                                str(self.ylen))
        script_content = script_content.replace('zlen = 0.01', 'zlen = ' + 
                                                str(self.zlen))
        script_content = script_content.replace('smallBox_factor = 3',
                                                'smallBox_factor = ' +
                                                str(self.smallBox_factor))
        script_content = script_content.replace('bixBox_factor = 11',
                                                'bixBox_factor = ' +
                                                str(self.bigBox_factor))
        script_content = script_content.replace('main_Meash_min = 0.00001',
                                                'main_Meash_min = ' +
                                                str(self.main_Mesh_min))
        script_content = script_content.replace('main_mesh_max = 1',
                                                'main_mesh_max = ' +
                                                str(self.main_mesh_max))
        script_content = script_content.replace('object_Mesh_max = 0.005',
                                                'object_Mesh_max = ' +
                                                str(self.object_Mesh_max))

        # Write the modified script content back to the same file
        with open(file_path_modifies, 'w') as file:
            file.write(script_content)

    def set_element_Specs(self, element_specs_path):
        
        # TODO:: if needet auto mate element settings
        self.element_specs_path = element_specs_path

    def modify_element_specs(self, current_script_dir):
        

        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.element_specs_path)

        file_path_modifies = os.path.join(current_script_dir,
                                          "operations_Files/" +
                                          str(self.projectName) + ".krn")

        # Read the original script content
        with open(file_path, 'r') as file:
            script_content = file.read()

        # Wr ite themodified script content back to the same file
        with open(file_path_modifies, 'w') as file:
            file.write(script_content)

    def set_sim_slurm(self, slurm_path, number_cores, mem_GB, gpu):
        self.slurm_path = slurm_path
        self.number_cores = number_cores
        self.mem_GB = mem_GB
        self.qpu = gpu
    
    """def modify_sim_slurm(self, current_script_dir):

        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.slurm_path)

        file_path_modifies = os.path.join(current_script_dir,"operations_Files/" + str(self.projectName) + ".slurm")

        # Read the original script content
        with open(file_path, 'r') as file:
            script_content = file.read()

        script_content = script_content.replace('MODELNAME="<model>"', 'MODELNAME="' + str(self.projectName)+ '"')
        script_content = script_content.replace('<description>', str(self.projectName))
        script_content = script_content.replace('--mem=8G', '--mem=' + str(self.mem_GB) )
        script_content = script_content.replace('--cpus-per-task=1', '--cpus-per-task=' + str(self.number_cores) )
        script_content = script_content.replace('--constraint=nv12', '--constraint=' + str(self.qpu) )
        # Wr ite themodified script content back to the same file
        with open(file_path_modifies, 'w') as file:
            file.write(script_content)"""

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
            '--mem=8G': f'--mem={self.mem_GB}',
            '--cpus-per-task=1': f'--cpus-per-task={self.number_cores}',
            '--constraint=nv12': f'--constraint={self.qpu}'
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


    def set_salome_slurm(self, slurm_salome_path, number_cores, mem_GB):
        self.slurm_salome_path = slurm_salome_path
        self.number_cores = number_cores
        self.mem_GB = mem_GB
    
    def modify_salome_slurm(self, current_script_dir):

        # Construct the full path by joining the directory path and filename
        file_path = os.path.join(current_script_dir, self.slurm_salome_path)

        file_path_modifies = os.path.join(current_script_dir,
                                          "operations_Files/salome.slurm")

        # Read the original script content
        with open(file_path, 'r') as file:
            script_content = file.read()

        logging.debug(f"Modifying salome slurm file: {file_path}")
        script_content = script_content.replace('--job-name="salome_equi_n128_dirac75_2nm"', '--job-name="' + str(self.projectName) + '"')
        script_content = script_content.replace('mem-per-cpu=8', 'mem-per-cpu=' + str(self.mem_GB) )
        script_content = script_content.replace('--cpus-per-task=4', '--cpus-per-task=' + str(self.number_cores) )
        script_content = script_content.replace('"$SLURM_SUBMIT_DIR"/step2_salome_macroFullLM_2nm.py', '"$SLURM_SUBMIT_DIR"/salome_mesh.py')
        script_content = script_content.replace('step2_salome_macroFullLM_2nm.py', 'salome_mesh.py')
    
        # Wr ite themodified script content back to the same file
        with open(file_path_modifies, 'w') as file:
            file.write(script_content)

    def get_project_name(self):
        return self.projectName
            
    def print_shape_info(self):
        print(f"Project Name: {self.projectName}")
        print(f"Box Dimensions: xlen={self.xlen}, ylen={self.ylen}, zlen={self.zlen}")
        print(f"Small Box Factor: {self.smallBox_factor}, Big Box Factor: {self.bigBox_factor}")
        print(f"Mesh Settings: main_Mesh_min={self.main_Mesh_min}, main_mesh_max={self.main_mesh_max}, object_Mesh_max={self.object_Mesh_max}")
        print(f"Simulation Settings: mx={self.mx}, my={self.my}, mz={self.mz}, hstart={self.hstart}, hfinal={self.hfinal}, hstep={self.hstep}, mfinal={self.mfinal}, mstep={self.mstep}")
        print(f"Field: hx={self.hx}, hy={self.hy}, hz={self.hz}")
        print(f"Minimizer: tol_fun={self.tol_fun}, cg_method={self.cg_method}, precond_iter={self.precond_iter}, hmag_on={self.hmag_on}, print_hmag={self.print_hmag}, verbose={self.verbose}")
        print(f"File Paths: p2_file_path={self.p2_file_path}, box_modifyer_path={self.box_modifyer_path}, element_specs_path={self.element_specs_path}")
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
                file.write(f"File Paths: p2_file_path={self.p2_file_path}, box_modifyer_path={self.box_modifyer_path}, element_specs_path={self.element_specs_path}\n")
                file.write(f"Slurm Paths: sim_slurm_path={self.slurm_path}, salome_slurm_path={self.slurm_salome_path}\n")
                
            print(f"Box information saved to '{file_path}'")

    def disturbe_shape(self, percent=5):
        #randmly add or subracts up to 5 % of value
        self.xlen = self.xlen + self.xlen * np.random.uniform(-percent/100, percent/100)
        self.ylen = self.ylen + self.ylen * np.random.uniform(-percent/100, percent/100)
        self.zlen = self.zlen + self.zlen * np.random.uniform(-percent/100, percent/100)

#creats an default box which can be mofifyed with the needed param
def creat_default_box(config: Config):
    box = Box(config.simulation.sim_name)
    #--------define shape of box-----------------

    box_modifyer_path = os.path.join(config.generalSettings.location, "prerequisits/src/box_creator.py")
    #target box size (this is the magnet)
    xlen = config.simulation.init_xlen
    ylen = config.simulation.init_ylen
    zlen = config.simulation.init_zlen
    #air box scaliing factors
    smallBox_factor = 3 #>0
    bixBox_factor = 11   #>smallBox_factor
    #mesh param
    main_Meash_min = 0.1
    main_mesh_max = 1.0
    object_Mesh_max = 0.8

    box.setGeometrySettings(xlen, ylen, zlen, smallBox_factor, bixBox_factor, main_Meash_min, main_mesh_max, object_Mesh_max, box_modifyer_path)
    #------- define simulation settings-----------
    p2_file_path = os.path.join(config.generalSettings.location, "prerequisits/_template_.p2")

    #[initial state]
    mx = 0.
    my = 0.
    mz = 1.
    #[field]
    hstart = 0.001
    hfinal = 0.0
    hstep = -0.001
    mfinal = -0.5
    mstep = 0.5
    hx = 0.034
    hy = 1.0
    hz = 0.0
    #[minimizer] 
    tol_fun = 1.0e-10
    cg_method = 1004
    precond_iter = 10
    hmag_on = 1
    print_hmag = 0
    verbose = 0
    box.set_sim_settings(mx, my, mz, hstart, hfinal, hstep, mfinal, mstep, hx, hy, hz, tol_fun, cg_method, precond_iter, hmag_on, print_hmag, verbose, p2_file_path)
    #----------- modify element specs (<project>.krn)-----------
    #So far automation is not woth the time since they wont change much
    element_specs_path = os.path.join(config.generalSettings.location,"prerequisits/_template_.krn")
    box.set_element_Specs(element_specs_path)
    #--------- modify sim slurm-------------
    slurm_path = os.path.join(config.generalSettings.location,"prerequisits/_template_.slurm")
    number_cores = 1
    mem_GB = 12
    gpu = 'nv12'
    box.set_sim_slurm(slurm_path, number_cores, mem_GB, gpu)
    #--------- modify salome slurm-------------
    slurm_salome_path = os.path.join(config.generalSettings.location,"prerequisits/salome.slurm")
    number_cores = 1
    mem_GB = 12
    box.set_salome_slurm(slurm_salome_path, number_cores, mem_GB)
    return box







