from storage.client.local import LocalClient
from storage.client.minio import MinIOClient

clients = {None: LocalClient, "Local": LocalClient, "MinIO": MinIOClient}
