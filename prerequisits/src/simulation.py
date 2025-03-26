
import os
import subprocess
import sys
import time
import shutil
import logging
import time

from prerequisits.src.shape import *






class Simmulation():
    def __init__(self, shape,  location, iter=1):
        """
        This function orchestrates the entire simulation workflow for a given geometric shape.
        It encompasses several steps including preprocessing, mesh generation, transformation of mesh format,
        and execution of the microMag simulation job. The function ensures all necessary directories and files are
        set up correctly and manages the submission of jobs to a simulation engine (e.g., Salome for mesh generation).

        Args:
            shape (Shape): An object representing the geometry of the simulation. This object should provide
                        methods for generating necessary simulation files and retrieving the project name.
            logger (Logger): An object used for logging messages throughout the simulation process. This logger
                            should support various levels of messages (e.g., info, error).
            location (str): The location where the simulation files are stored.
            iter (int): The number of iterations to run the simulation. Important mostly for output storrage
            results (Results): An object to store the results of the simulation.

        Returns:
            None

        """
        self.shape = shape
        self.logger = logging.getLogger(__name__)
        
        self.location = location
        self.resluts = None

        # Save slum ID for acces of the output files
        self.microMag_SlurmID = None
        self.salome_SlurmID = None
        self.iter = iter


    def run_Simulation(self):
        """
        The function performs the following major steps:
        1. Preprocessing setup: Creation of necessary directories and verification of prerequisite files.
        2. File generation: Execution of scripts to generate simulation files specific to the 'shape'.
        3. Mesh generation: Submission of a mesh generation job to Salome and transformation of the mesh format.
        4. Simulation execution: Submission of the microMag simulation job and management of its output.

        Throughout the process, the function logs progress and important information, facilitating debugging and monitoring.
        It also performs checks at each stage to ensure the workflow can proceed, halting with descriptive error messages
        if necessary conditions are not met.
        """

        # Preprocessing setup
        self.logger.debug("Starting preprocessing setup...")
        self.delete_and_create_folder("operations_Files")
        self.create_directory_if_not_exists(f"output")
        self.create_directory_if_not_exists(f"output/graphics")
        self.creat_file_if_not_exist("output/labels.txt")
        self.delete_and_create_folder(f"output/{self.iter}")  

        # Check for required files
        self.logger.debug("Checking for required files in the 'prerequisits' directory...")
        self.make_all_files_in_dir_executable("prerequisits" )
        if not (self.check_files_in_folder("prerequisits", ["_template_.krn", "_template_.p2", "_template_.slurm", "tofly3"])):
            sys.exit(1)
        if not self.check_files_in_folder("prerequisits/src", ["box_creator.py", "shape.py", "simulation.py"]):
            sys.exit(1)
        self.logger.debug("All required files found in the 'prerequisits' directory.")


        # Execute templet_modify.py to generate files for the specific shape
        self.logger.debug("Generating files for the specific shape...")
        self.generate_files_for_shape()
        project_name = self.shape.get_project_name()

        if not project_name:
            self.logger.error("Project name is empty. Exiting.")
            sys.exit(1)

        # Mesh generation with Salome and format transformation
        self.logger.info("Starting mesh generation with Salome...")
        salome_job_id = self.run_salome_mesh_generation(project_name )
        self.salome_SlurmID = salome_job_id

        # Collect results from Salome
        self.create_directory_if_not_exists(f"output/{self.iter}/salome" )
        self.move_simulation_output(f"{self.location}/operations_Files/results/slurm-{salome_job_id}", f"{self.location}/output/{self.iter}/salome")
        self.check_folder_exists(f"{self.location}/output/{self.iter}/salome/slurm-{salome_job_id}" )
        
        self.logger.debug("Mesh generation complete. Transforming mesh format with tofly3...")
        os.system(f"{self.location}/prerequisits/tofly3 -e 1,2 {self.location}/operations_Files/mesh.unv {self.location}/operations_Files/{project_name}.fly")

        # Check if essential files exist and make them accessible for simulation
        self.check_and_make_accessible(["slurm", "fly", "p2", "krn"],project_name)

        # Start the microMag simulation
        self.logger.info(f"All preliminary checks passed. Starting the microMag simulation with {project_name}.slurm...")
        self.logger.info(f"Curretn shape: {self.shape.get_info_shape()}")
        
        microMag_job_id, run_time = self.submit_job_and_wait(f"{self.location}/operations_Files/{project_name}.slurm")
        self.microMag_SlurmID = microMag_job_id
        self.logger.info(f"microMag simulation job completed in {run_time/60} min.")

        # collect results from microMag job
        self.create_directory_if_not_exists(f"output/{self.iter}/microMag" )
        self.move_simulation_output(f"{self.location}/operations_Files/output/slurm_{microMag_job_id}", f"{self.location}/output/{self.iter}/microMag")
        self.check_folder_exists(f"{self.location}/output/{self.iter}/microMag/slurm_{microMag_job_id}" )

        # also collect al the operational files 
        self.create_directory_if_not_exists(f"output/{self.iter}/operations_Files" )
        self.move_simulation_output(f"{self.location}/operations_Files", f"{self.location}/output/{self.iter}/operations_Files")
        self.check_folder_exists(f"{self.location}/output/{self.iter}/operations_Files" )

        # move logs
        #create_directory_if_not_exists(f"output/{self.iter}/logs" )
        #move_simulation_output(f"{self.location}/logs", f"{self.location}/output/{self.iter}/logs", self.logger)
        #check_folder_exists(f"{self.location}/output/{self.iter}/logs" )

        # clean up


        self.logger.info("Simulation workflow completed successfully. :<)")


    def get_microMag_SlurmID(self):
        return self.microMag_SlurmID
    
    def get_salome_SlurmID(self):
        return self.salome_SlurmID

    
    def creat_file_if_not_exist(self, file_name, header= " "):
        """
        Create a file if it does not already exist.

        Args:
            file_path (str): The path of the file to create.
            logger: The logger object to log the status.

        Returns:
            None
        """
        folder_path = os.path.join(self.location, file_name)
        if not os.path.exists(folder_path):
            with open(folder_path, 'w') as file:
                #self.logger.debug(f"Created file: {folder_path}")
                file.write(header)


    def delete_and_create_folder(self, folder_name):
        """
        Deletes an existing folder and creates a new one with the given name.
        """
        folder_path = os.path.join(self.location, folder_name)
        if os.path.exists(folder_path):
            #self.logger.debug(f"Deleting existing folder bevor: {folder_path}")
            shutil.rmtree(folder_path)  # This deletes the directory and all its contents
            self.logger.debug(f"Deleted existing folder: {folder_path}")
        os.makedirs(folder_path)
        #self.logger.debug(f"Created Folder: {folder_path}")

    def create_directory_if_not_exists(self, folder_name ):
        """
        Create a directory if it does not already exist.

        Args:
            directory_path (str): The path of the directory to create.
            logger: The logger object to log the status.

        Returns:
            None
        """
        folder_path = os.path.join(self.location, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.logger.debug(f"Created Folder: {folder_path}")

    def make_all_files_in_dir_executable(self, folder_name):
        """
        Make all files in the given directory and its subfolders executable and readable.

        Args:
            folder_name (str): The name of the folder containing the files.
            location (str): The base location where the folder is located.
            logger: The logger object to log the status.

        Returns:
            None
        """
        folder_path = os.path.join(self.location, folder_name)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.chmod(file_path, 0o755)  # Set executable permission
                #self.logger.debug(f"Made file executable and readable: {file_path}")

    def check_files_in_folder(self, folder_name, file_names):
        """
        Check if all the specified files exist in the given folder.

        Args:
            folder_name (str): The name of the folder to check.
            location (str): The base location where the folder is located.
            file_names (list): A list of file names to check for existence.
            logger: The logger object to log error and info messages.

        Returns:
            None
        """
        folder_path = os.path.join(self.location, folder_name)

        # Logging the folder path being checked
        self.logger.debug(f"Checking for files in: {folder_path}")

        missing_files = [file for file in file_names if not os.path.isfile(os.path.join(folder_path, file))]
        if missing_files:
            for file in missing_files:
                full_path = os.path.join(folder_path, file)
                self.logger.error(f"File does not exist: {full_path}")  # Log the full path of the missing file
                # Optionally, return or yield the full path if you want to collect these paths for further processing
                # return full_path
                # or
                # yield full_path
            return False
            #sys.exit(1)
        self.logger.debug(f"All required files exist: {file_names}")
        return True

    def check_folder_exists(self, folder_name):
        """
        Check if a folder exists in the given location.

        Args:
            folder_name (str): The name of the folder to check.
            location (str): The base location where the folder is located.
            logger: The logger object to log the status.

        Returns:
            None
        """
        folder_path = os.path.join(self.location, folder_name)
        if not os.path.exists(folder_path):
            self.logger.error(f"Folder does not exist: {folder_path}")
            sys.exit(1)
        self.logger.debug(f"Folder exists: {folder_path}")

    def generate_files_for_shape(self):
        """
        Generate files for a given shape.

        Args:
            shape: The shape object for which files need to be generated.
            logger: The logger object for logging messages.

        Raises:
            Exception: If there is an error in the input parameters.

        Returns:
            None
        """
        
        self.shape.apply_all_modifications(self.location)


    def run_salome_mesh_generation(self, project_name, repeat=3): 
        """
        Generates mesh using Salome.

        Args:
            project_name (str): The name of the project.
            repeat (int): Number of times to attempt mesh generation if it fails.

        Returns:
            int: The job ID of the Salome mesh generation process if successful.
        """
        file_path_salome = os.path.join(self.location, "operations_Files/salome_mesh.py")
        file_path_slurm = os.path.join(self.location, "operations_Files/salome.slurm")

        # Check if the Salome script file exists
        if not os.path.isfile(file_path_salome):
            self.logger.error(f"Salome script file '{file_path_salome}' does not exist.")
            sys.exit(1)
        
        # Check if the Slurm file exists
        if not os.path.isfile(file_path_slurm):
            self.logger.error(f"Slurm file '{file_path_slurm}' does not exist.")
            sys.exit(1)

        # Change file permissions for Slurm script
        try:
            subprocess.run(["chmod", "+r", file_path_slurm], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to change permissions for '{file_path_slurm}': {e}")
            sys.exit(1)

        self.logger.debug("Initiating mesh generation with Salome...")



        self.logger.debug("Initiating mesh generation with Salome...")

        # Attempt mesh generation up to 'repeat' times
        for attempt in range(1, repeat + 1):
            try:
                salome_job_id, run_time = self.submit_job_and_wait(file_path_slurm)
                self.logger.info(f"Salome mesh generation completed in {run_time / 60:.2f} minutes (Attempt {attempt}/{repeat}).")
            
                # Check if the expected output file exists
                if self.check_files_in_folder("operations_Files", ["mesh.unv"]):
                    self.logger.debug(f"Mesh generation successful after {attempt} attempt(s).")
                    return salome_job_id
                else:
                    self.logger.warning(f"Mesh generation attempt {attempt} failed. File 'mesh.unv' not found.")
            
            except Exception as e:
                self.logger.error(f"An error occurred during mesh generation attempt {attempt}: {e}")

        # If we reach here, all attempts have failed
        self.logger.error(f"Mesh generation failed after {repeat} attempts.")
        sys.exit(1)



    def submit_job_and_wait(self, job_file):
        """
        Submits a job file to the system using `sbatch` command and waits for the job to complete.

        Args:
            job_file (str): The path to the job file to be submitted.
            logger: The logger object used for logging.

        Returns:
            str: The job ID of the submitted job.
            float: The time it took to run the job in seconds.
        """
        # Save the current directory
        original_dir = os.getcwd()
        
        # Navigate to the job file's directory
        job_dir = os.path.dirname(job_file)
        os.chdir(job_dir)
        
        # Submit the job
        job_id = subprocess.getoutput(f"sbatch --parsable {os.path.basename(job_file)}").strip()
        self.logger.info(f"Job with JOBID: {job_id} started")
        
        # Navigate back to the original directory
        os.chdir(original_dir)
        
        # Wait for the job to complete
        start_time = time.time()
        while True:
            result = subprocess.run(f"squeue | grep {job_id}", capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                break
            else:
                time.sleep(3)

        elapsed_time = time.time() - start_time
        
        return job_id, elapsed_time

    def check_and_make_accessible(self, file_suffixes, project_name):
        """
        Check if files with specified suffixes exist and are not empty in the given directory.
        If a file is found to be empty or does not exist, an error is logged and the program exits.

        Args:
            file_suffixes (list): List of file suffixes to check.
            base_dir (str): Base directory path.
            project_name (str): Name of the project.
            logger (Logger): Logger object for logging messages.

        Returns:
            None
        """
        for suffix in file_suffixes:
            file_path = f"{self.location}/operations_Files/{project_name}.{suffix}"
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                os.chmod(file_path, 0o755)
                self.logger.debug(f"File {file_path} exists and is not empty.")
            else:
                self.logger.error(f"File {file_path} does not exist or is empty.")
                sys.exit(1)

    def move_simulation_output(self, folder_to_move, target_folder):
        """
        Moves the simulation output folder and its subfolders to the specified target folder.

        Args:
            folder_to_move (str): The path of the folder to be moved.
            target_folder (str): The path of the target folder where the folder will be moved to.
            logger: The logger object used for logging messages.

        Raises:
            FileNotFoundError: If the folder to be moved does not exist.

        Returns:
            None
        """
        if os.path.exists(folder_to_move):
            shutil.move(folder_to_move, target_folder)
            self.logger.debug(f"Moving simulation output folder '{folder_to_move}' to the '{target_folder}' directory...")
        else:
            self.logger.error(f"Folder {folder_to_move} does not exist. Skipping move operation.")
            sys.exit(1)




    