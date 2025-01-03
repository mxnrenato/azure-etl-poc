from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file (for local development)
load_dotenv()

# Key Vault configuration
AZURE_KEY_VAULT_URL = os.getenv("AZURE_KEY_VAULT_URL")  # e.g., "https://your-vault.vault.azure.net/"

def get_secrets():
    """Retrieve secrets from Azure Key Vault or fallback to environment variables"""
    try:
        # Initialize the Secret Client
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=AZURE_KEY_VAULT_URL, credential=credential)

        # Fetch secrets from Key Vault
        secrets = {
            "AZURE_STORAGE_CONNECTION_STRING": secret_client.get_secret("azure-storage-connection-string").value,
            "AZURE_BLOB_CONTAINER_ROW_DATA": secret_client.get_secret("azure-blob-container-row-data").value,
            "AZURE_BLOB_CONTAINER_BACKUPS": secret_client.get_secret("azure-blob-container-backups").value,
            "AZURE_SQL_CONNECTION_STRING": secret_client.get_secret("azure-sql-connection-string").value,
        }
        print("Successfully loaded secrets from Azure Key Vault")
        return secrets

    except Exception as e:
        print(f"Failed to load secrets from Key Vault: {str(e)}")
        print("Falling back to environment variables")
        # Fallback to environment variables
        return {
            "AZURE_STORAGE_CONNECTION_STRING": os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
            "AZURE_BLOB_CONTAINER_ROW_DATA": os.getenv("AZURE_BLOB_CONTAINER_ROW_DATA"),
            "AZURE_BLOB_CONTAINER_BACKUPS": os.getenv("AZURE_BLOB_CONTAINER_BACKUPS"),
            "AZURE_SQL_CONNECTION_STRING": os.getenv("AZURE_SQL_CONNECTION_STRING"),
        }

# Load secrets
secrets = get_secrets()

# Assign secrets to variables
AZURE_STORAGE_CONNECTION_STRING = secrets["AZURE_STORAGE_CONNECTION_STRING"]
AZURE_BLOB_CONTAINER_ROW_DATA = secrets["AZURE_BLOB_CONTAINER_ROW_DATA"]
AZURE_BLOB_CONTAINER_BACKUPS = secrets["AZURE_BLOB_CONTAINER_BACKUPS"]
AZURE_SQL_CONNECTION_STRING = secrets["AZURE_SQL_CONNECTION_STRING"]

# Validate required variables
if not all(
    [
        AZURE_STORAGE_CONNECTION_STRING,
        AZURE_BLOB_CONTAINER_ROW_DATA,
        AZURE_BLOB_CONTAINER_BACKUPS,
        AZURE_SQL_CONNECTION_STRING,
    ]
):
    raise ValueError("One or more required environment variables or secrets are missing!")