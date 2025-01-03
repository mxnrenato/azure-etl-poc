from src.application.interfaces.storage_service import StorageService
from azure.storage.blob import BlobServiceClient
from typing import BinaryIO


class AzureBlobStorageService(StorageService):
    def __init__(self, connection_string: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_name = "etl-data"

    def sanitize_blob_name(filename: str) -> str:
        # Remueve caracteres no válidos
        invalid_chars = ['\\', '/', '#', '?']
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Reemplaza espacios con guiones bajos o remueve
        filename = filename.replace(' ', '_')

        # Verifica si termina con un punto y lo remueve
        if filename.endswith('.'):
            filename = filename[:-1]

        return filename


    async def store_file(self, file_content: BinaryIO, filename: str) -> bool:
        """Store file in Azure Blob Storage"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(filename)
            file_content.seek(0)
            blob_client.upload_blob(file_content, overwrite=True)
            print(f"[INFO] File '{filename}' successfully stored in container '{self.container_name}'.")
            return True
        except Exception as e:
            print(f"[ERROR] Error storing file '{filename}': {str(e)}")
            return False


    async def retrieve_file(self, filename: str) -> BinaryIO:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=filename
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            print(f"Error retrieving file: {str(e)}")
            raise
