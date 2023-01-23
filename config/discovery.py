"""
This module is responsible for the discovery of the cluster nodes.
"""
import logging
import socket

from zeroconf import ServiceInfo

from config.env import env
from config.logger import log

# Set logging
logging.getLogger("zeroconf").setLevel(log.level)

# Define service parameters
hostname = socket.gethostname()
fqdn_name = f"{hostname}.{env.cluster.fqdn_service}"
host_ip = socket.gethostbyname(hostname)

properties = {"cluster": env.cluster.name, "version": env.cluster.version}
service = ServiceInfo(
    env.cluster.fqdn_service,
    f"{hostname}.{env.cluster.fqdn_service}",
    env.cluster.port,
    parsed_addresses=[host_ip],
    # Setting DNS TXT records...
    properties=properties,
)
