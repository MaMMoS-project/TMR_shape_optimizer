from prerequisits.src.optimizer import *
import logging.config
import json
import sys
from pathlib import Path

# scp -r /home/fillies/Documents/UWK_Projects/TMR_shape_optimizer/* fillies@scandium:/ceph/home/fillies/tmr_sensors/simplebox/UCB/restart_test/.
#nohup python3 main.py > logs/output.log 2>&1 & echo $! > logs/pid.txt &
#watch -n 1 'squeue -u fillies'
#tail -f logs/output.log



# In your main or any other module
def main() -> None:
    location = os.path.dirname(os.path.abspath(__file__))

    # Load the configuration

    config = load_config(location=location, config_name="FM.yaml")

        # set location of simulation to the location of the main.py file
    config.generalSettings.location = location

    setup_logging(log_level=config.generalSettings.log_level, base_dir= config.generalSettings.location )  

    # log config
    logging.debug(f"Configuration loaded: {config}")

    optimizer = Optimizer(locattion=config.generalSettings.location ,
                          max_Iter=config.simulation.iter)

    # creat object e.g. free layer of sensor
    optimizer.creat_shape(config)  # only saves the values to the shape does not apply any chages to the files
    #optimizer.creat_real_box(config) 
    # from here on the optimizer knows the shape
    
    # initialize bay optimizer
    optimizer.bayesian_optimization_setup(config)
    logging.debug("Optimization setup done")

    if config.database.use_DB:
        optimizer.setup_database(config.database)
    else:
        logging.info("No database used")

    optimizer.optimize() # runs the optimization changes the file to desired.




# In your main or any other module
def mesh_ana() -> None:
    location = os.path.dirname(os.path.abspath(__file__))

    # Load the configuration

    config = load_config(location=location, config_name="3FMsmall.yaml")

        # set location of simulation to the location of the main.py file
    config.generalSettings.location = location

    setup_logging(log_level=config.generalSettings.log_level, base_dir= config.generalSettings.location )  

    # log config
    logging.debug(f"Configuration loaded: {config}")

    logging.info("Mesh analysis started")

    #object_Mesh_max: 5e-3  
    min_mesh = 1e-0
    max_mesh = 9e-2
    steps = 50
    all_mesh = np.logspace(np.log10(min_mesh), np.log10(max_mesh), num=steps)
    logging.info(f" Analyzing mesh sizes from {min_mesh} to {max_mesh} with {steps} steps")


    for mesh in all_mesh:
        try:
            logging.info(f"Mesh analysis with mesh factor size: {mesh  }")
            #config.simulation.object_Mesh_max = config.shape.init_xlen  # Set the mesh size proportional to the object size
            config.simulation.x_direction_max_mesh = config.simulation.x_direction_max_mesh * mesh
            config.simulation.y_direction_max_mesh = config.simulation.y_direction_max_mesh * mesh

            logging.info(f"Mesh size set to: {config.simulation.object_Mesh_max, config.simulation.x_direction_max_mesh, config.simulation.y_direction_max_mesh}")

            optimizer = Optimizer(locattion=config.generalSettings.location , config=config,
                          max_Iter=config.simulation.iter)

            # creat object e.g. free layer of sensor
            optimizer.creat_shape(config)  # only saves the values to the shape does not apply any chages to the files
            #optimizer.creat_real_box(config) 
            # from here on the optimizer knows the shape
            
            # initialize bay optimizer
            optimizer.bayesian_optimization_setup(config)
            logging.debug("Optimization setup done")

            if config.database.use_DB:
                optimizer.setup_database(config.database)
            else:
                logging.info("No database used")

            optimizer.optimize(mesh) # runs the optimization changes the file to desired.


        except Exception as e:
            logging.error(f"Error in mesh analysis: {e}")
            continue







def single_postprocess():
    threshhold_training=0.5
    margin_to_line=0.05
    #print(threshhold_training, margin_to_line)
    temp_post = PostProc(threshhold_training, margin_to_line )
    temp_post.load_file_singe('/home/fillies/Documents/UWK_Projects/TMR_shape_optimizer/data/2D_test.dat')
    temp_post.linear_regression(regression_restart_counter = 0)
    temp_post.anasyse_data()
    temp_post.plot_data()









if __name__ == "__main__":
    #main()
    #single_postprocess()
    mesh_ana()
    