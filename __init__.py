import signal
from typing import Union

from config.env import env
from config.logger import log
from config.models.env import StorageConfig
from role.discovery import ObjectStashCoordinator

# Need a way to make following some kind of default storage in config
from storage import clients
from storage.models.client import StorageClient


class GracefulExit:
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        print("CTRL+C captured, exiting gracefully (repeat to exit now)")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state


class StorageManager:
    def __init__(self, client: StorageClient):
        self.client = client
        if not client.container_exists():
            log.debug(f"{client.container} not found in storage; creating container")
            done = client.create_container()
            if not done:
                raise Exception(f"Could not create {client.container} container")
        log.debug(f"Initializing with the {client.container} container")

    def database(self):
        pass

    def filesystem(self):
        pass


class ObjectStash:
    def __init__(self):
        self.coordinator = ObjectStashCoordinator()
        self.flag = GracefulExit()

    def connect(self, storage_name: str) -> StorageClient:
        storage: Union[StorageConfig, None] = env.storage.get(storage_name, None)
        client: Union[StorageClient, None] = clients.get(storage_name, None)
        if not client:
            raise Exception(f"{storage_name} not found in available storage clients")
        if not storage:
            raise Exception(f"{storage_name} not found in config")

        try:
            instance: StorageClient = client(**storage.dict())
            return instance
        except Exception as e:
            raise Exception(f"{storage_name} initialisation failed: {e}")

    def __del__(self):
        del self.coordinator
        return self.flag


if __name__ == "__main__":
    objsth = ObjectStash()
    client = objsth.connect("Local")
    client_mgr = StorageManager(client)
    client_mgr.database()
    client_mgr.filesystem()
