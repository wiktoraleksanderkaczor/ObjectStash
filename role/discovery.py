from typing import Union

from pydantic import AnyUrl
from zeroconf import ServiceBrowser  # , ZeroconfServiceTypes
from zeroconf import ServiceInfo, ServiceListener, Zeroconf

from ..config.discovery import service, stype
from ..config.env import env
from .distribution import Distributed

# Find all services
# print('\n'.join(ZeroconfServiceTypes.find()))


class ObjectStashListener(ServiceListener):
    def update_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        info: Union[ServiceInfo, None] = zc.get_service_info(type_, name)
        if info:
            print(f"Service {name} updated, service info: {info}")

    def remove_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        info: Union[ServiceInfo, None] = zc.get_service_info(type_, name)
        if info:
            print(f"Service {name} removed, service info: {info}")
            Distributed.peers.remove(name)
            for obj in Distributed.distributed_objects:
                obj.removeNodeFromCluster(name)

    def add_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        info: Union[ServiceInfo, None] = zc.get_service_info(type_, name)
        if type_ != stype:
            return
        if info:
            if info.properties.get("cluster", "") != env.cluster.name:
                return
            print(f"Service {name} added, service info: {info}")
            Distributed.peers.append(name)
            for obj in Distributed.distributed_objects:
                obj.addNodeToCluster(name)


class ObjectStashCoordinator:
    def __init__(self) -> None:
        # Initialise zeroconf and listeners
        self.zeroconf = Zeroconf(interfaces=["0.0.0.0"])
        self.listener = ObjectStashListener()
        self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self.listener)

        # Register service
        self.service = service
        self.zeroconf.register_service(self.service, cooperating_responders=True)

    def __del__(self):
        self.zeroconf.unregister_service(self.service)
        self.zeroconf.close()
        del self
