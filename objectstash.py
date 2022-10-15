import signal

from .discovery import ObjectStashCoordinator
from .env import container_name
from .logger import log
from .storage import storage


class GracefulExit():
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        print('CTRL+C captured, exiting gracefully (repeat to exit now)')
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state


class ObjectStash():
    def __init__(self):
        try:
            self.coordinator = ObjectStashCoordinator()
            if not storage.container_exists(container_name):
                log.debug(
                    f'{container_name} not found in storage; creating container')
                done = storage.create_container(container_name)
                if not done:
                    raise Exception(
                        f"Could not create {container_name} container")
            log.debug(f'Initializing with the {container_name} container')
        except Exception as e:
            log.exception(f'ObjectStash initialisation failed because; {e}')
            raise e
        self.flag = GracefulExit()

    def __del__(self):
        del self.coordinator
        return self.flag
