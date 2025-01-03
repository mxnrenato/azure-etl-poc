# settings.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER_ROW_DATA = os.getenv("AZURE_BLOB_CONTAINER_ROW_DATA")
AZURE_BLOB_CONTAINER_BACKUPS = os.getenv("AZURE_BLOB_CONTAINER_BACKUPS")
AZURE_SQL_CONNECTION_STRING = os.getenv("AZURE_SQL_CONNECTION_STRING")

# Validate required variables
if not all(
    [
        AZURE_STORAGE_CONNECTION_STRING,
        AZURE_BLOB_CONTAINER_ROW_DATA,
        AZURE_BLOB_CONTAINER_BACKUPS,
        AZURE_SQL_CONNECTION_STRING,
    ]
):
    raise ValueError("One or more required environment variables are missing!")
