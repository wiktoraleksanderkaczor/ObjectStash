import signal
from typing import Union

from config.env import env
from config.logger import log
from config.models.env import StorageConfig
from role.discovery import ObjectStashCoordinator

# Need a way to make following some kind of default storage in config
from storage import clients
from storage.client.models.client import StorageClient


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
        if not client.container_exists(client.container):
            log.debug(f"{client.container} not found in storage; creating container")
            done = client.create_container(client.container)
            if not done:
                raise Exception(f"Could not create {client.container} container")
        log.debug(f"Initializing with the {client.container} container")

    def database():
        pass

    def filesystem():
        pass


class ObjectStash:
    def __init__(self):
        self.coordinator = ObjectStashCoordinator()
        self.flag = GracefulExit()

    def connect(storage_name: str) -> Union[StorageClient, None]:
        storage: StorageConfig = env.storage.get(storage_name)
        client = clients.get(storage_name, None)
        if not client or storage:
            log.debug(f"{storage_name} not found in available storage clients and/or configuration")
            return None

        try:
            instance: StorageClient = client(
                storage.container, storage.region, storage.secure, storage.access_key, storage.secret_key
            )
            return instance
        except Exception as e:
            log.error(f"{storage_name} initialisation failed: {e}")
            return None

    def __del__(self):
        del self.coordinator
        return self.flag


if __name__ == "__main__":
    objsth = ObjectStash()
    client = objsth.connect("Local")
    client_mgr = StorageManager(client)
    client_mgr.database()
    client_mgr.filesystem()
