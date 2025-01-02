from application.interfaces.storage_service import StorageService
from azure.storage.blob import BlobServiceClient
from typing import BinaryIO

class AzureBlobStorageService(StorageService):
    def __init__(self, connection_string: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = "etl-data"

    async def store_file(self, file_content: BinaryIO, filename: str) -> bool:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            file_content.seek(0)  # Reset file pointer to beginning
            blob_client.upload_blob(file_content, overwrite=True)
            return True
        except Exception as e:
            print(f"Error storing file: {str(e)}")
            return False

    async def retrieve_file(self, filename: str) -> BinaryIO:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            print(f"Error retrieving file: {str(e)}")
            raise