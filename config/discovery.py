import socket

from zeroconf import ServiceInfo

from .env import env
from .logger import level, logging

# Set logging
logging.getLogger("zeroconf").setLevel(level)

# Define service parameters
base = "objectstash"
extension = "local."
stype = "_http._tcp"
base_name = f"{base}.{extension}"
full_name = f"{base_name}.{stype}.{extension}"
port = env.cluster.port
host_ip = socket.gethostbyname(socket.gethostname())

properties = {"cluster": env.cluster.name}
service = ServiceInfo(
    stype,
    full_name,
    server=base_name,
    parsed_addresses=[host_ip],
    port=port,
    # Setting DNS TXT records...
    properties=properties,
)
