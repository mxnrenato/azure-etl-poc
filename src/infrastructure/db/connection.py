import pyodbc
from contextlib import contextmanager
from settings import AZURE_SQL_CONNECTION_STRING

def get_db_connection():
    """
    Creates and returns a new database connection using the connection string from settings.
    """
    if not AZURE_SQL_CONNECTION_STRING:
        raise ValueError("Database connection string is not available in settings.")

    try:
        conn = pyodbc.connect(AZURE_SQL_CONNECTION_STRING)
        return conn
    except Exception as e:
        raise ConnectionError(f"Failed to connect to the database: {str(e)}")

@contextmanager
def get_db_cursor():
    """
    Context manager that provides a database cursor and handles connection cleanup.
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            rows = cursor.fetchall()
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

# Optional: Verify connection on module load
if __name__ == "__main__":
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
        print("Database connection test successful!")
    except Exception as e:
        print(f"Database connection test failed: {str(e)}")