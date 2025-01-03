from azure.storage.blob import BlobServiceClient
from abc import ABC, abstractmethod
from typing import BinaryIO
from src.application.interfaces.storage_service import StorageService


class AzureBlobStorageServiceInfrastructure(StorageService):
    def __init__(self, connection_string: str, container_name: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_name = container_name

    async def store_file(self, file_content: BinaryIO, filename: str) -> bool:
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(filename)
            file_content.seek(0)
            blob_client.upload_blob(file_content, overwrite=True)
            print(
                f"[INFO] File '{filename}' successfully stored in container '{self.container_name}'."
            )
            return True
        except Exception as e:
            print(f"[ERROR] Error storing file '{filename}': {str(e)}")
            return False

    async def retrieve_file(self, filename: str) -> BinaryIO:
        """Retrieve file from Azure Blob Storage"""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(filename)
            blob_data = blob_client.download_blob()
            print(
                f"[INFO] File '{filename}' successfully retrieved from container '{self.container_name}'."
            )
            return blob_data.content_as_bytes()
        except Exception as e:
            print(f"[ERROR] Error retrieving file '{filename}': {str(e)}")
            raise
