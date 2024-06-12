from prerequisits.src.optimizer import *
import logging.config
import json
import sys
from pathlib import Path

# scp -r /home/fillies/Documents/UWK_Projects/TMR_sensors/* fillies@scandium:/ceph/home/fillies/tmr_sensor_sensors/automatization/y/config_test_2/
#nohup python3 main.py > logs/output.log 2>&1 & echo $! > logs/pid.txt &



# In your main or any other module
def main() -> None:
    location = os.path.dirname(os.path.abspath(__file__))

    # Load the configuration
    config = load_config(location=location, config_name="testConfig.yaml")

    # set location of simulation to the location of the main.py file
    config.generalSettings.location = location

    setup_logging(log_level=config.generalSettings.log_level, base_dir= config.generalSettings.location )  

    # Access configuration
    #print(config)
    # log config
    logging.info(f"Configuration loaded: {config}")

    optimizer = Optimizer(locattion=config.generalSettings.location ,
                          max_Iter=config.simulation.iter)
    #optimizer.create_default_box()
    optimizer.creat_real_box(config) # only saves the values to the box does not apply any chages to the files
    
    # initialize bay optimizer
    if config.database.use_DB:
        optimizer.bayesian_optimization_setup()


    #db_path = '/home/fillies/Documents/UWK_Projects/tmr_sensor_sensors/autoSim/Database/box414.db'
    if config.database.use_DB:
        optimizer.setup_database(config.database)
    else:
        logging.info("No database used")
        #test

    optimizer.optimize() # runs the optimization changes the file to desired.







def single_postprocess():
    threshhold_training=0.5
    margin_to_line=0.05
    #print(threshhold_training, margin_to_line)
    temp_post = PostProc(threshhold_training, margin_to_line )
    temp_post.load_file('/home/fillies/Documents/UWK_Projects/tmr_sensor/autoSim/localVersion/operations_Files/02m020001.dat')
    #temp_post.load_file('/home/fillies/Documents/UWK_Projects/tmr_sensor/autoSim/postProcesses/1_m1_trueBox.dat')
    temp_post.linear_regression()
    temp_post.anasyse_data()
    temp_post.plot_data()









if __name__ == "__main__":
    main()
    #single_postprocess()
