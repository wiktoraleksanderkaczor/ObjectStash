import socket

from zeroconf import ServiceInfo

from .env import env
from .logger import level, logging

# Set logging
logging.getLogger("zeroconf").setLevel(level)

# Define service parameters
base_name = "objectstash.local."
stype = "_http._tcp.local."
name = "%s.%s" % (base_name.split(".")[0], stype)
port = env["CLUSTER"]["PORT"]
host_ip = socket.gethostbyname(socket.gethostname())

properties = {"container": env["STORAGE"]["CONTAINER"]}
service = ServiceInfo(
    stype,
    name,
    server=base_name,
    address=host_ip,
    port=port,
    # Setting DNS TXT records...
    properties=properties,
)
