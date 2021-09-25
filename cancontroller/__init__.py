import os
import os.path
import json
import dataclasses
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

logs_dir = os.path.join(ROOT_DIR, "logs")
if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)


@dataclasses.dataclass
class Configuration:
    grpc_port: int = 50051
    http_server_port: int = 8080
    can_bus_speed: int = 500000
    can_bus: str = "can1"
    can_log_filename: str = "can_log_file.asc"
    controller_log_filename: str = "controller_log_file.log"

    def get_controller_log_file(self):
        return os.path.join(logs_dir, self.controller_log_filename)

    def get_can_log_file(self):
        return os.path.join(logs_dir, self.can_log_filename)

try:
    with open("/home/pi/Controller/config.json", "r+") as fp:
        configuration = Configuration(**json.load(fp))
except Exception as e:
    print("Failed to load configuration from file: ", e)
    configuration = Configuration()