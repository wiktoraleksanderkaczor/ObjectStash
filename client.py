import signal
from typing import Type, Union

from config.env import env
from config.logger import log
from config.models.env import StorageConfig
from role.superclass.discovery import Coordinator
from storage.interface.client import StorageClient


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
        self.client: StorageClient = client
        log.debug(f"Initializing with the {client.config.repository} repository")

    def database(self):
        pass

    def filesystem(self):
        pass


class ObjectStash:
    def __init__(self):
        self.coordinator = Coordinator()
        self.flag = GracefulExit()

    def connect(self, config: Union[str, StorageConfig], client: Type[StorageClient]) -> StorageClient:
        settings: Union[StorageConfig, None] = None
        if isinstance(config, str):
            settings = env.storage.get(config, None)
        else:
            settings = config

        if not settings:
            raise Exception(f"{config} not found in settings or arguments")

        # client: Union[Type[StorageClient], None] = StorageClient.subclasses.get(storage_name, None)
        if not client:
            raise Exception(f"{config} not found in available storage clients")

        try:
            instance: StorageClient = client(settings)
            return instance
        except Exception as e:
            raise Exception(f"{client.__name__} initialisation failed: {e}")

    def __del__(self):
        del self.coordinator
        return self.flag


if __name__ == "__main__":
    objsth = ObjectStash()
    from storage.client.local import LocalClient

    client = objsth.connect("Local", LocalClient)
    client_mgr = StorageManager(client)
    client_mgr.database()
    client_mgr.filesystem()
