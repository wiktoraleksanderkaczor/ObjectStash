import signal

from config.env import container_name, env
from config.logger import log
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


class ObjectStash:
    def __init__(self, client: str = env["STORAGE"]["CLIENT"]):
        try:
            client: StorageClient = clients[client]
            self.coordinator = ObjectStashCoordinator()
            if not client.container_exists(container_name):
                log.debug(f"{container_name} not found in storage; creating container")
                done = client.create_container(container_name)
                if not done:
                    raise Exception(f"Could not create {container_name} container")
            log.debug(f"Initializing with the {container_name} container")
        except Exception as e:
            log.exception(f"ObjectStash initialisation failed because; {e}")
            raise e
        self.flag = GracefulExit()

    def __del__(self):
        del self.coordinator
        return self.flag
