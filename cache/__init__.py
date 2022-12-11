from cache.caches.database import Database
from cache.caches.storage import Storage

clients = {"Partition": Database, "Storage": Storage}
