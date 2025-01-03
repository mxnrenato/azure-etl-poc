from dotenv import load_dotenv
import os
import pyodbc

load_dotenv()
AZURE_SQL_CONNECTION_STRING = os.getenv("AZURE_SQL_CONNECTION_STRING")

def get_db_connection():
    """
    Creates and returns a new database connection using the connection string from the environment.
    """
    connection_string = os.getenv(AZURE_SQL_CONNECTION_STRING)
    if not connection_string:
        raise ValueError("Database connection string is not set in the environment.")
    
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        raise ConnectionError(f"Failed to connect to the database: {str(e)}")

get_db_connection()

