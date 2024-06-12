
# B4Vex Simulation Project

The B4Vex Simulation Project is designed to simulate various aspects of a sensor system, focusing on single simulations, interval-based simulations, and in the future, optimization-based simulations. The project's core is built around a Python-based framework, making extensive use of modular components for easy customization and extension.

## Project Structure

The project consists of several key components organized as follows:

- `main.py`: The entry point of the simulation project. It currently triggers single and interval simulations. Future updates will include optimization capabilities.
- `logging_config`: Configuration file(s) for logging purposes to help in debugging and tracking the simulation process.
- `prerequisites`: Essential files and templates needed for the simulation to run. This includes:
  - Various templates required for different parts of the simulation.
  - `tofly3`: A specialized module or data set specific to this project.
  - `src`: Contains Python source files critical to the simulation process.
    - `simulation.py`: Describes the B4Vex simulation process in detail.
    - `settings.py`: Configures the parameters for the sensor to be simulated.
    - `interval.py`: Contains classes to simulate a parameter interval, crucial for interval-based simulations.
    - Additional Python files that support the simulation process.

## Getting Started

### Prerequisites

Before running the simulation, ensure that your environment is set up with the necessary dependencies. These can include but are not limited to:

- Python 3.x
- Relevant Python libraries (e.g., NumPy, Matplotlib) for computation and visualization
- Any specific hardware or software requirements dictated by `tofly3` or other modules

### Installation

1. Clone the repository or download the project files to your local machine.
2. Navigate to the project directory.
3. Install the required Python dependencies using pip:

   ```sh
   pip install -r requirements.txt
   ```

4. Configure the `logging_config` as needed to suit your debugging and logging preferences.

### Running a Simulation

To start a simulation, simply run the `main.py` script:

```sh
python main.py
```

Currently, the `main.py` script supports single and interval simulations. You can modify this script to adjust the simulation parameters or to add new types of simulations as the project evolves.

## Simulation Details

- **Single Simulations**: Aimed at analyzing specific scenarios or configurations without varying parameters extensively.
- **Interval Simulations**: Focus on varying parameters within specified intervals to understand the sensor's behavior under different conditions.
- **Optimization (Future Work)**: Intended to identify the optimal parameters for desired outcomes using various optimization techniques.

## Contributing

Contributions to the B4Vex Simulation Project are welcome. Whether it's feature enhancements, bug fixes, or documentation improvements, your help is appreciated. Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.




DATAbase
setup database individually. since there are only few different combinations of shape and meshing parameters these will stay manually. It also helps to keep track of databases.
each database has ha sahke like box and meshing parameters like 
box.main_Mesh_min = 0.1
box.main_mesh_max = 1.0
box.object_Mesh_max = 0.8

each box is discribed via three maram xlen, ylen, zlen

output parameter:
len of lin demagnetizatuion curve

path
since all different instances are supposed to acces the same databases i will acces them with a absolut path
