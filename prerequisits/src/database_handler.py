import sqlite3
import logging

class DatabaseHandler:
    def __init__(self, db_path, postProc_golbal_path):
        """
        Initializes a DatabaseHandler object.

        Args:
            db_path (str): Abs path to the database. This will stay abs since alls the simulation will acces the same database. and its location is not relatet to the location of the of the simulation.

        Attributes:
            logger (logging.Logger): The logger object for logging messages.
            db_path (str): The path to the database file.
            postProc_golbal_path (str): The path to the post processing folder here the plot of the post processes will be saved
            conn (sqlite3.Connection): The connection object for the database.
            cursor (sqlite3.Cursor): The cursor object for executing SQL queries.

        Raises:
            sqlite3.Error: If there is an error connecting to the database.

        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug("DatabaseHandler object created")

        self.db_path = db_path
        self.postProc_golbal_path = postProc_golbal_path
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.logger.debug(f"Connected to the database at {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect to the database: {e}")

     
        
    def query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def query_and_count(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return self.cursor.rowcount  # Returns the number of rows inserted
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None  # Indicates that the insert failed
    
    def close(self):
        self.conn.close()

    def get_postProc_golbal_path(self):
        return self.postProc_golbal_path

        



