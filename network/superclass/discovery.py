"""
Discovery role superclass
"""
import ipaddress
import logging
import socket
from typing import Dict, Optional

from pydantic import AnyUrl
from zeroconf import ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf

from distribution.superclass.distributed import Distributed
from network.interface.discovery import CoordinatorInterface, ListenerInterface

# Set logging
from reporting.logger import logger

logging.getLogger("zeroconf").setLevel(logger.level)


class Listener(ListenerInterface, ServiceListener):
    def __init__(self, service_info: ServiceInfo) -> None:
        self.service_info = service_info
        super().__init__()

    def update_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        info: Optional[ServiceInfo] = zc.get_service_info(type_, str(name))
        if info:
            print(f"Service {name} updated, service info: {info}")

    def remove_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        info: Optional[ServiceInfo] = zc.get_service_info(type_, str(name))
        if info:
            print(f"Service {name} removed, service info: {info}")
            Distributed.peers.remove(name)

    def add_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        info: Optional[ServiceInfo] = zc.get_service_info(type_, str(name))
        if not info:
            return

        # Validate service type
        if type_ != self.service_info.type:
            return

        # Validate IP address
        addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
        addresses = [addr for addr in addresses if not ipaddress.ip_address(addr).is_loopback]
        if not addresses:
            return

        # Decode properties
        properties: Dict[str, Optional[str]] = {}
        for k, v in info.properties.items():
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            properties[k] = v  # type: ignore

        # Validate cluster name
        hostname = self.service_info.name.split(".")[0]
        if properties.get("node", "") == hostname:
            return

        # Add service to list of peers
        print(f"Service {name} added, service info: {info}")
        Distributed.peers.add(name)


class Coordinator(CoordinatorInterface):
    def __init__(self, service_name: str, port: int = 9091) -> None:
        # Define service parameters
        self.hostname = socket.gethostname()
        self.fqdn: str = f"_{service_name}._tcp.local."

        # Create service
        self.service = ServiceInfo(
            type_=self.fqdn,
            name=f"{self.hostname}.{self.fqdn}",
            port=port,
            parsed_addresses=[socket.gethostbyname(self.hostname)],
            # Setting DNS TXT records...
            properties={"node": self.hostname},
        )

        # Initialise zeroconf and listeners
        self.zeroconf = Zeroconf(interfaces=["0.0.0.0"])
        self.listener = Listener(self.service)
        self.browser = ServiceBrowser(self.zeroconf, self.fqdn, self.listener)

        # Register service
        self.zeroconf.register_service(self.service, cooperating_responders=True)

    def query_service(self, type_: str, name: str) -> Optional[ServiceInfo]:
        return self.zeroconf.get_service_info(type_, name)

    def __del__(self):
        self.zeroconf.unregister_service(self.service)
        self.zeroconf.close()
        del self
