import logging
import logging.config
import json
import logging.handlers
import random
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import qmc
import os


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

def append_line_to_file(file_path, param, label):
    """
    Appends a line to a file with the specified file path, 
    ensuring it starts on a new line if the last line is not empty.

    Args:
        file_path (str): The path of the file to append the line to.
        param (str): The parameter to append to the file.
        label (str): The label to append to the file.
    """
    try:
        newline_needed = False

        # Check if the last character in the file is not a newline
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'rb') as f:
                f.seek(-1, os.SEEK_END)
                last_char = f.read(1)
                if last_char != b'\n':
                    newline_needed = True

        with open(file_path, 'a') as file:
            if newline_needed:
                file.write('\n')
            line = f"{param} {label}\n"
            file.write(line)
            logging.debug(f"Appended line to {file_path}: {line.strip()}")

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



class Random_Suggestor:
    """
    Generates random Values for beanchmark testing
    """
    def __init__(self, xStart, xEnd, yStart, yEnd, zStart, zEnd):
        self.bounds = {
            "xlen": [xStart, xEnd],
            "ylen": [yStart, yEnd],
            "zlen": [zStart, zEnd]
        }

    def generate_random(self):
        return {
            "xlen": random.uniform(self.bounds["xlen"][0], self.bounds["xlen"][1]),
            "ylen": random.uniform(self.bounds["ylen"][0], self.bounds["ylen"][1]),
            "zlen": random.uniform(self.bounds["zlen"][0], self.bounds["zlen"][1]),
        }
    




class Grid_Suggestor:
    """
    Generates random values or grid points for benchmark testing.
    """
    def __init__(self, xStart, xEnd, yStart, yEnd, zStart, zEnd, iterations, known_maxima=(1.928, 0.1, 0.02), include_boundaries=False):
        logging.info(f"Initializing Grid_Suggestor") 
        self.bounds = {
            "xlen": [xStart, xEnd],
            "ylen": [yStart, yEnd],
            "zlen": [zStart, zEnd]
        }
        self.iterations = iterations
        self.include_boundaries = include_boundaries
        self.grid_points = []
        self.distances = []
        self.current_index = 0
        self.known_maxima = known_maxima

        self._generate_grid()
        self._calculate_distances()

    def _generate_grid(self):
        """Generates grid points for the specified bounds."""
        num_points_per_dimension = int(np.ceil((self.iterations) ** (1/3)))
        logging.info(f"Total Number of grid points: {num_points_per_dimension**3}")

        if self.include_boundaries:
            x_range = np.linspace(
                self.bounds["xlen"][0],
                self.bounds["xlen"][1],
                num_points_per_dimension
            )
            y_range = np.linspace(
                self.bounds["ylen"][0],
                self.bounds["ylen"][1],
                num_points_per_dimension
            )
            z_range = np.linspace(
                self.bounds["zlen"][0],
                self.bounds["zlen"][1],
                num_points_per_dimension
            )
        else:
            # Exclude boundaries accurately
            x_range = np.linspace(
                self.bounds["xlen"][0],
                self.bounds["xlen"][1],
                num_points_per_dimension + 2
            )[1:-1]
            y_range = np.linspace(
                self.bounds["ylen"][0],
                self.bounds["ylen"][1],
                num_points_per_dimension + 2
            )[1:-1]
            z_range = np.linspace(
                self.bounds["zlen"][0],
                self.bounds["zlen"][1],
                num_points_per_dimension + 2
            )[1:-1]

        self.grid_points = [
            {"xlen": x, "ylen": y, "zlen": z}
            for x in x_range
            for y in y_range
            for z in z_range
        ]

    def _calculate_distances(self):
        """Calculates distances of all grid points to the known maxima relative to coordinate intervals."""
        x_interval = self.bounds["xlen"][1] - self.bounds["xlen"][0]
        y_interval = self.bounds["ylen"][1] - self.bounds["ylen"][0]
        z_interval = self.bounds["zlen"][1] - self.bounds["zlen"][0]

        self.distances = [
            (
                np.sqrt(
                    ((point["xlen"] - self.known_maxima[0]) / x_interval)**2 +
                    ((point["ylen"] - self.known_maxima[1]) / y_interval)**2 +
                    ((point["zlen"] - self.known_maxima[2]) / z_interval)**2
                ),
                idx
            )
            for idx, point in enumerate(self.grid_points)
        ]
        self.distances.sort(key=lambda x: x[0])

    def get_num_grid_points(self):
        """Returns the number of grid points generated."""
        return len(self.grid_points)

    def next_grid_point(self):
        """
        Suggests the next grid point based on precomputed distances.

        Returns:
            dict: The next closest grid point.

        Raises:
            IndexError: If no more grid points are available.
        """
        if self.current_index >= len(self.distances):
            raise IndexError("No more grid points available.")

        closest_index = self.distances[self.current_index][1]
        self.current_index += 1

        return self.grid_points[closest_index]

    def print_grid_points(self):
        """Prints and plots each grid point in a 3D plot."""
        # Print all grid points
        print("Grid Points:")
        for i, pt in enumerate(self.grid_points):
            print(f"{i}: x={pt['xlen']:.4f}, y={pt['ylen']:.4f}, z={pt['zlen']:.4f}")



class Plane_Suggestor:
    """
    Generates uniform grid points within the XY plane for a fixed Z-value.
    """
    def __init__(self, xStart, xEnd, yStart, yEnd, zValue, iterations, include_boundaries=True):
        self.bounds = {
            "xlen": [xStart, xEnd],
            "ylen": [yStart, yEnd]
        }
        self.zValue = zValue
        self.iterations = iterations
        self.include_boundaries = include_boundaries
        self.grid_points = []
        self.current_index = 0

        self._generate_grid()

    def _generate_grid(self):
        """Generates grid points for the XY plane at the specified Z-value."""
        num_points_per_dimension = int(np.ceil(np.sqrt(self.iterations)))

        if self.include_boundaries:
            x_range = np.linspace(
                self.bounds["xlen"][0],
                self.bounds["xlen"][1],
                num_points_per_dimension
            )
            y_range = np.linspace(
                self.bounds["ylen"][0],
                self.bounds["ylen"][1],
                num_points_per_dimension
            )
        else:
            # Exclude boundaries accurately
            x_range = np.linspace(
                self.bounds["xlen"][0],
                self.bounds["xlen"][1],
                num_points_per_dimension + 2
            )[1:-1]
            y_range = np.linspace(
                self.bounds["ylen"][0],
                self.bounds["ylen"][1],
                num_points_per_dimension + 2
            )[1:-1]

        self.grid_points = [
            {"xlen": x, "ylen": y, "zlen": self.zValue}
            for x in x_range
            for y in y_range
        ]

    def get_num_grid_points(self):
        """Returns the number of grid points generated."""
        return len(self.grid_points)

    def next_grid_point(self):
        """
        Suggests the next grid point.

        Returns:
            dict: The next available grid point.

        Raises:
            IndexError: If no more grid points are available.
        """
        if self.current_index >= len(self.grid_points):
            raise IndexError("No more grid points available.")

        point = self.grid_points[self.current_index]
        self.current_index += 1

        return point
