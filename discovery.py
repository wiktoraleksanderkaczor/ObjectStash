import logging
import socket

# Find all services
# print('\n'.join(ZeroconfServiceTypes.find()))
from zeroconf import ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf, ZeroconfServiceTypes

from .distribution import Distributed
from .env import env
from .logger import level

# Set logging
logging.getLogger("zeroconf").setLevel(level)

# Define service parameters
base_name = "objectstash.local."
stype = "_http._tcp.local."
name = "%s.%s" % (base_name.split(".")[0], stype)
port = env["CLUSTER"]["PORT"]
host_ip = socket.gethostbyname(socket.gethostname())


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
        properties = {"container": env["STORAGE"]["CONTAINER"]}
        self.service = ServiceInfo(
            stype,
            name,
            server=base_name,
            address=host_ip,
            port=port,
            # Setting DNS TXT records...
            properties=properties,
        )
        self.zeroconf.register_service(self.service, cooperating_responders=True)

    def __del__(self):
        super().__del__()
        self.zeroconf.unregister_service(self.service)
        self.zeroconf.close()
