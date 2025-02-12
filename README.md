
# B4Vex Simulation Project

The B4Vex Simulation Project is designed to simulate various aspects of a sensor system, focusing on single simulations, interval-based simulations, and in the future, optimization-based simulations. The project's core is built around a Python-based framework, making extensive use of modular components for easy customization and extension.

## Project Structure

The project consists of several key components organized as follows:

### Main Components

- **`main.py`**: The entry point of the simulation project. It has two main functions:
  1. **main()**: Triggers the entire optimization cycle.
     - Ensure you set up your attended configuration (e.g., `config = load_config(location=location, config_name="set10.yaml")`).
  2. **single_postprocess()**: Triggers post-processing on an individual Demag Curve.
     - Used to test and develop post-processes.
     - Saves .dat file in the Data folder (e.g., `temp_post.load_file_singe('/home/fillies/Documents/UWK_Projects/TMR_shape_optimizer/data/2D_test.dat')`).

### Logging Configuration

- **`logging_config`**: Configuration file(s) for logging purposes to help in debugging and tracking the simulation process.

### Logs

- **`logs`**: Directory containing log files.
  - **`master.log`**: Stores the logs with the log level set in the configuration (usually high).
  - **`output.log`**: Stores all the output in the command line (same logs as in master but with a low log level).
  - **`pid.txt`**: Stores process ID of the optimization run, which can be helpful in case of a detached terminal.

### Data

- **`data`**: Stores .dat demag curves files for individual post-process analysis.

### Prerequisites

- **`prerequisites`**: Essential files and templates needed for the simulation to run. This includes:
  - **`configs`**: Used to configure an optimization cycle. Will be called by `main.py`.
    1. **`database`**: Has to be set up on the server you want to run your simulations on. Not required. Paths have to stay global.
    2. **`shape`**: Set shape type (so far only box possible). Changing the mesh parameters is possible but not advisable.
    3. **`simulation`**: Change the name to keep a good overview of your running processes. Set parameter interval + starting values to your desire. `h*` describes the outer magnetic field. A small hstep speeds everything up but also increases accuracy. Too small, and you will get in trouble with the post-processes.
  - Various templates required for different parts of the simulation.
    - **`_template_.krn`**: Defines the material properties.
    - **`_template_.p2`**: Defines the outer magnetic field.
    - **`_template_.slurm`**: B4Vex simulation SLURM template.
    - **`salome.slurm`**: Salome SLURM job template.
  - **`tofly3`**: A specialized module or dataset specific to this project.
  - **`src`**: Contains Python source files critical to the simulation process.
    - **`box_creator.py`**: Salome script for creating and meshing the box. Will be modified by `settings.py` for the specific shape of the box and meshing parameters.
    - **`configuration.py`**: Reads the configuration file specified in `main.py`.
    - **`simulation.py`**: Describes the B4Vex simulation process in detail.
    - **`database_handler.py`**: Handles connections to the database.
    - **`helper.py`**: Contains mostly logging functions.
    - **`optimizer.py`**: Performs the optimization. Sets up the database and triggers post-processes. The `optimize()` function is the heart of the whole project.
    - **`templet_modify.py`**: Configures the parameters for the sensor in `box_creator.py` to be simulated.
    - **`postProc.py`**: Performs post-processes. So far, it performs linear fits around 0+ and determines how long the demag curves stay within a defined margin for plotting.

## Files that will be created during Simulations

### operations_File (used in current or last iteration)
- Contains all the (previously modified) actually used templates described above.
- `___.unv`: Result from meshing. (So far, I cannot import this to Salome again. If you find a way, please let me know.)
- `___.fly`: UNV file transformed to FLY format.

### results
- Contains results from every optimization iteration.
  - **`labels.txt`**: Overview of all labels and their parameters from all the simulation iterations.
  - **`graphics`**: All the plots of successful post-processes.
  - **`integer 1-x`**: Results from each iteration of optimization.
    - **`operationsal_Files`**: See above.
    - **`main`**: Results from B4Vex simulation.
      - `__.dat`: Most important file of simulation to be analyzed by post-processes.
    - **`salome`**: Results from Salome meshing.



### Running a Simulation

1. Create a configuration file in `prerequisites` according to your requirements. And name is according to your simname **`readme_eg.yaml`**.
  ```yaml
    (...)
    simulation:
    sim_name: 'readme_eg'
    (...)
  ```

2. Configure the config file path in `main.py`.
  ```py
    (...)
    config = load_config(location=location, config_name="readme_eg.yaml")
    (...)

3. Copy your project to an remote server.

4. Run `main.py` as follows:
   ```sh
   nohup python3 main.py > logs/output.log 2>&1 & echo $! > logs/pid.txt &




## License

This project is licensed under the MIT License - see the `LICENSE` file for details.




### DATAbase
setup database individually. since there are only few different combinations of shape and meshing parameters these will stay manually. It also helps to keep track of databases.
each database has ha sahke like box and meshing parameters like 
box.main_Mesh_min = 0.1
box.main_mesh_max = 1.0
box.object_Mesh_max = 0.8

each box is discribed via three maram xlen, ylen, zlen

output parameter:
len of lin demagnetizatuion curve

Creat your own Database:
sqlite3 new_box504.db
CREATE TABLE shapes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    xlen REAL,
    ylen REAL,
    zlen REAL,
    linDis REAL
);


