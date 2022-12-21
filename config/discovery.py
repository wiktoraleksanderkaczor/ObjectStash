import socket

from zeroconf import ServiceInfo

from config.env import env
from config.logger import level, logging

# Set logging
logging.getLogger("zeroconf").setLevel(level)

# Define service parameters
fqdn_service = "_objectstash._tcp.local."
hostname = socket.gethostname()
fqdn_name = f"{hostname}.{fqdn_service}"
host_ip = socket.gethostbyname(hostname)

properties = {"cluster": env.cluster.name, "version": env.cluster.version}
service = ServiceInfo(
    fqdn_service,
    f"{hostname}.{fqdn_service}",
    env.cluster.port,
    parsed_addresses=[host_ip],
    # Setting DNS TXT records...
    properties=properties,
)
