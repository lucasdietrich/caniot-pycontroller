import json
import dataclasses


@dataclasses.dataclass
class Configuration:
    grpc_port: int = 50051
    http_server_port: int = 8080
    can_bus_speed: int = 500000
    can_bus: str = "can1"
    log_file: str = "logfile.asc"

try:
    with open("/home/pi/Controller/config.json", "r+") as fp:
        configuration = Configuration(**json.load(fp))
except Exception as e:
    print("Failed to load configuration from file: ", e)
    configuration = Configuration()