from abc import ABC, abstractmethod
import pandas as pd 
import logging
from prerequisits.src.configuration import OptimizerConfig
from prerequisits.src.shape import Shape

class AbstractPostProc(ABC):
    """
    Abstract base class for post-processing of simulation data.
    """
    
    def __init__(self,  shape: Shape = None, iter: int = -1):
        """
        Initializes the AbstractPostProc class with necessary configurations and parameters.
        """
        #self.config = config
        #self.params = params
        #self.iter = iter
        self.shape = shape
        #self.results = Results()
        self.data: pd.DataFrame = None
        self.df_training: pd.DataFrame = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.shape_info, self.shape_name = self._initialize_shape_info()
    
    def _initialize_shape_info(self):
        """Retrieves shape information safely, handling any exceptions."""
        if self.shape:
            try:
                return self.shape.get_info_shape(), self.shape.get_project_name()
            except AttributeError:
                self.logger.warning("Shape object lacks required methods.")
        return ["unknown shape"] * 3, "unknown shape"

    @abstractmethod
    def calc_label(self) -> float:
        """
        Computes a label for the post-processing task.
        """
        pass

    @abstractmethod
    def plot_postProc(self):
        """
        Generates a visualization of the post-processing results.
        """
        pass

    @abstractmethod
    def save_postProc_plot(self, location: str, iter: int, full_path: bool = True):
        """
        Saves the generated post-processing plot to a specified file location.
        """
        pass

    @abstractmethod
    def load_file(self, location: str, iter: int, micromag_ID: str, project_Name: str) -> pd.DataFrame:
        """
        Loads simulation data from a file and stores it in a DataFrame.
        """
        pass
