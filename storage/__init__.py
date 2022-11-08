from storage.client.local import LocalClient
from storage.client.minio import MinIOClient

clients = {"Local": LocalClient, "MinIO": MinIOClient}
