"""Private Blob storage for DXF files. The container is private; files leave only through
this service, which checks the API key first. Authentication uses the Container App's
managed identity, so no storage keys are stored anywhere."""

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class BlobStore:
    def __init__(self, account_url: str, container: str):
        client = BlobServiceClient(account_url, credential=DefaultAzureCredential())
        self._container = client.get_container_client(container)

    def get_base_dxf(self, product_id: str, size: str) -> bytes | None:
        name = f"base/{product_id}/{size}.dxf"
        try:
            return self._container.download_blob(name).readall()
        except ResourceNotFoundError:
            return None

    def put_dxf(self, name: str, data: bytes) -> None:
        self._container.upload_blob(name, data, overwrite=False)
