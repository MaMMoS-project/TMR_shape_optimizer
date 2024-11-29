import logging
import logging.config
import json
import logging.handlers
from pathlib import Path


# tHIS fiLE IS DESIGNED FOR ADDITIONAL SMALL CLASSES AND FUNCTIONS

def get_valid_log_level(level):
    """ Convert level to a valid log level; if invalid, default to INFO """
    if isinstance(level, int):
        if level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            return level
    elif isinstance(level, str):
        try:
            return getattr(logging, level.upper())
        except AttributeError:
            pass
    print("Invalid log level: {}. Defaulting to INFO.".format(level))
    return logging.INFO

def setup_logging(log_level: int, base_dir, log_file="master.log", max_size=10*1024*1024, backup_count=5):
    base_dir = Path(base_dir)
    logs_dir = base_dir / 'logs'
    logging_config_file = base_dir / 'logging_configs' / 'stdout-file.json'

    logs_dir.mkdir(exist_ok=True)
    log_file_path = logs_dir / log_file

    try:
        with open(logging_config_file) as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Logging configuration file not found.")
        return
    except json.JSONDecodeError:
        print("Logging configuration file contains invalid JSON.")
        return

    if 'file' in config['handlers']:  # Check if 'file' handler exists in config
        # Update file handler to RotatingFileHandler with new settings
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': logging.getLevelName(get_valid_log_level(log_level)),  # Validate and set log level
            'formatter': 'standard',
            'filename': str(log_file_path),
            'mode': 'a',
            'maxBytes': max_size,
            'backupCount': backup_count,
        }

    logging.config.dictConfig(config)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.info("Logging configured successfully.")

def append_line_to_file(file_path, param, label, config, slome_runtime, micro_mag_runtime, num_tet ):
    """
    Appends a line to a file with the specified file path.

    Args:
        file_path (str): The path of the file to append the line to.
        param (str): The parameter to append to the file.
        label (str): The label to append to the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If any other error occurs while appending the line to the file.
    """
    try:
        with open(file_path, 'a') as file:
            # if first appen header
            if file.tell() == 0:
                header = "object_Mesh_max | salome_runtime | micro_mag_runtime | num_tet label\n"
                file.write(header)
            line = f"{config.simulation.x_direction_max_mesh} {slome_runtime/60} {micro_mag_runtime/60} {num_tet} {label}\n"
            file.write(line)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
