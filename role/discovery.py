from zeroconf import ServiceBrowser  # , ZeroconfServiceTypes
from zeroconf import ServiceListener, Zeroconf

from ..config.discovery import service, stype
from ..config.env import env
from .distribution import Distributed

# Find all services
# print('\n'.join(ZeroconfServiceTypes.find()))


class ObjectStashListener(ServiceListener):
    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} updated, service info: {info}")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} removed, service info: {info}")
        Distributed.peers.remove(name)
        for obj in Distributed.distributed_objects:
            obj.removeNodeFromCluster(name)

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if type_ != stype:
            return
        if info.properties.get("container", "") != env["STORAGE"]["CONTAINER"]:
            return
        print(f"Service {name} added, service info: {info}")
        Distributed.peers.append(name)
        for obj in Distributed.distributed_objects:
            obj.addNodeToCluster(name)


class ObjectStashCoordinator:
    def __init__(self) -> None:
        # Initialise zeroconf and listeners
        self.zeroconf = Zeroconf("0.0.0.0")
        self.listener = ObjectStashListener()
        self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self.listener)

        # Register service

        self.service = service
        self.zeroconf.register_service(self.service, cooperating_responders=True)

    def __del__(self):
        super().__del__()
        self.zeroconf.unregister_service(self.service)
        self.zeroconf.close()
