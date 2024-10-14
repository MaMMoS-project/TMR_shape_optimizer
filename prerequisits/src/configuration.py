from pydantic import BaseModel
import yaml
import os

class DatabaseConfig(BaseModel):
    use_DB: bool
    read_only: bool
    name: str
    db_path: str
    postProc_global_path: str
    

class ShapeConfig(BaseModel):
    name: str
    main_Mesh_min: float
    main_mesh_max: float
    object_Mesh_max: float

class SimulationConfig(BaseModel):
    sim_name: str
    iter: int
    xlen_start: float
    xlen_stop: float
    ylen_start: float
    ylen_stop: float
    zlen_start: float
    zlen_stop: float
    hstart: float
    hfinal: float
    hstep: float
    init_xlen: float
    init_ylen: float
    init_zlen: float

class ServerConfig(BaseModel):
    number_cores: int
    mem_GB: int

class generalSettingsConfig(BaseModel):
    log_level: int
    location: str

class Optimizer(BaseModel):
    acq_kind: str
    kappa: float
    xi: float
    kappa_decay: float
    kappa_decay_delay: int

class Config(BaseModel):
    database: DatabaseConfig
    shape: ShapeConfig
    simulation: SimulationConfig
    server: ServerConfig
    generalSettings: generalSettingsConfig
    optimizer: Optimizer



#'/home/fillies/Documents/UWK_Projects/tmr_sensor_sensors/autoSim/localVersion/prerequisits/configs/testConfig.yaml'
def load_config(location: str, config_name: str) -> Config:
    config_file = os.path.join(location, "prerequisits/configs", config_name)
    with open(config_file, 'r') as file:
        config_data = yaml.safe_load(file)
        return Config(**config_data)



# Load the configuration
"""config = load_config('/home/fillies/Documents/UWK_Projects/tmr_sensors/autoSim/localVersion/prerequisits/configs/testConfig.yaml')

# Access configuration
print(config)

# Print individual sections
print("\nDatabase Config:")
print(config.database)
print("\nShape Config:")
print(config.shape)
print("\nSimulation Config:")
print(config.simulation)
print("\nServer Config:")
print(config.server)
print("\ngeneralSettings Config")
print(config.generalSettings)"""
