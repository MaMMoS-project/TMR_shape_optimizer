
import os
import subprocess
import sys
import time
import shutil
import logging
import time
import glob

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
        self.create_directory_if_not_exists(f"output/dat_files")
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
        salome_job_id, salome_runtime = self.run_salome_mesh_generation(project_name )
        self.salome_SlurmID = salome_job_id

        #
        
        
        self.logger.debug("Mesh generation complete. Transforming mesh format with tofly3...")
        os.system(f"{self.location}/prerequisits/tofly3 -e 1,2 {self.location}/operations_Files/mesh.unv {self.location}/operations_Files/{project_name}.fly")
        # run grep Tet4 *.fly 
        

        self.create_directory_if_not_exists(f"output/{self.iter}/salome" )
        self.move_simulation_output(f"{self.location}/operations_Files/mesh.unv", f"{self.location}/output/{self.iter}/salome")
        self.move_simulation_output(f"{self.location}/operations_Files/results/slurm-{salome_job_id}", f"{self.location}/output/{self.iter}/salome")
         #Collect results from Salome

        num_tet = self.get_tet4_count(self.location, self.salome_SlurmID)
        logging.info(f"Number of Tet4 elements: {num_tet}")
        
        
        self.check_folder_exists(f"{self.location}/output/{self.iter}/salome/slurm-{salome_job_id}" )
        
        
        

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

        self.move_and_rename_files_by_pattern(
            folder_to_search=f"{self.location}/output/{self.iter}/microMag/slurm_{microMag_job_id}",
            pattern="*.dat",
            target_folder=f"{self.location}/output/dat_files/",
            new_file_name_template=f"{self.iter}.dat" 
        )

 


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
        return salome_runtime,  run_time, num_tet

    """def get_tet4_count(self, location, project_name):
        # Construct the command
        command = f"grep Tet4 {location}/operations_Files/{project_name}.fly"
        try:
            # Run the command and capture the output
            result = subprocess.check_output(command, shell=True, text=True)
            # Extract the count (assuming the output is "Tet4 37700")
            count = result.split()[1]  # The second part should be the number
            logging.info(f"Number of Tet4 elements: {count}")
            return int(count)
        except subprocess.CalledProcessError as e:
            logging.error("Failed to retrieve Tet4 count")
            return None"""
        
        #f"{self.location}/output/{self.iter}/salome""""

    
    def get_tet4_count(self, location, salome_SlurmID):
        """
        Retrieves the Tet4 count from a specified text file.

        Args:
            location (str): Base location of the project files.
            iter_num (str or int): Iteration number or identifier for the output folder.

        Returns:
            int: The count of Tet4 elements, or None if retrieval fails.
        """
        # Construct the path to the txt file
        file_path = f"{location}/output/{self.iter}/salome/slurm-{salome_SlurmID}/tets_output.txt"
        self.check_folder_exists(f"output/{self.iter}/salome/slurm-{salome_SlurmID}" )
        self.check_files_in_folder(f"output/{self.iter}/salome/slurm-{salome_SlurmID}", ["tets_output.txt"])
        self.make_all_files_in_dir_executable(f"output/{self.iter}/salome/slurm-{salome_SlurmID}" )
        try:
            # Open the txt file and read its content
            with open(file_path, "r") as file:
                content = file.read()
            
            # Extract the count (assuming the format "Tets Size: 37700")
            count = content.split(":")[1].strip()  # Gets the number after "Tets Size: "
            
            # Log and return the count as an integer
            logging.info(f"Number of Tet4 elements in sensor: {count}")
            return int(count)
        except (FileNotFoundError, IndexError, ValueError) as e:
            logging.error(e)
            logging.error("Failed to retrieve Tet4 count from the text file")
            return None
    

    def get_microMag_SlurmID(self):
        return self.microMag_SlurmID
    
    def get_salome_SlurmID(self):
        return self.salome_SlurmID

    def set_results(self, results):
        self.results = results

    def get_results(self):
        return self.results
    
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
        logging.debug(f"Making all files in '{folder_path}' executable and readable...")
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.chmod(file_path, 0o755)  # Set executable permission
                self.logger.debug(f"Made file executable and readable: {file_path}")

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


    def run_salome_mesh_generation(self, project_name, repeat=1): 
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
        run_time = 0
        # Attempt mesh generation up to 'repeat' times
        for attempt in range(1, repeat + 1):
            try:
                salome_job_id, run_time = self.submit_job_and_wait(file_path_slurm)
                self.logger.info(f"Salome mesh generation completed in {run_time / 60:.2f} minutes (Attempt {attempt}/{repeat}).")
            
                # Check if the expected output file exists
                if self.check_files_in_folder("operations_Files", ["mesh.unv"]):
                    self.logger.debug(f"Mesh generation successful after {attempt} attempt(s).")
                    return salome_job_id, run_time 
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

    def move_and_rename_file(self, file_to_move, target_folder, new_file_name):
        """
        Moves a single file to the specified target folder and renames it.

        Args:
            file_to_move (str): The path of the file to be moved.
            target_folder (str): The path of the target folder where the file will be moved to.
            new_file_name (str): The new name for the file in the target folder.

        Raises:
            FileNotFoundError: If the file to be moved does not exist.

        Returns:
            None
        """
        # Check if the file exists
        if os.path.isfile(file_to_move):
            # Define the full path for the renamed file in the target folder
            target_path = os.path.join(target_folder, new_file_name)
            
            # copy and rename the file
            shutil.copy(file_to_move, target_path)
            self.logger.debug(f"Moved and renamed file '{file_to_move}' to '{target_path}'.")
        else:
            # Log an error and exit if the file does not exist
            self.logger.error(f"File '{file_to_move}' does not exist. Skipping move and rename operation.")
            sys.exit(1)

    def move_and_rename_files_by_pattern(self, folder_to_search, pattern, target_folder, new_file_name_template):
        """
        Finds files matching a pattern in a specified folder, moves each file to the target folder, 
        and renames them according to a provided template.

        Args:
            folder_to_search (str): The folder in which to search for files.
            pattern (str): The filename pattern to search for (e.g., "*.dat").
            target_folder (str): The path of the target folder where files will be moved.
            new_file_name_template (str): Template for renaming files, with `{index}` for unique naming.

        Returns:
            None
        """
        # Search for files matching the pattern
        files = glob.glob(os.path.join(folder_to_search, pattern))

        if not files:
            self.logger.error(f"No files matching '{pattern}' found in '{folder_to_search}'.")
            return

        # Move and rename each file
        for index, file_path in enumerate(files, start=1):
            new_file_name = new_file_name_template.format(index=index)
            self.move_and_rename_file(file_path, target_folder, new_file_name)



    