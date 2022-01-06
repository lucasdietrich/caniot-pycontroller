from cancontroller.caniot.models import MsgId, DeviceId
from cancontroller.caniot.device import Device

from cancontroller.caniot.nodes.garage_door_controller import GarageDoorController

from typing import Dict, List, Union, Optional

node_garage_door = GarageDoorController(DeviceId(DeviceId.Class.CRTHPT, 0x02), "GarageDoorControllerProdPCB")

class Devices:
    """
    List all nodes on the current Bus
    """
    def __init__(self):
        self.devices = [
            node_garage_door
        ]

    def get(self, name: str):
        for dev in self.devices:
            if dev.name == name:
                return dev

    def __getitem__(self, name: str):
        return self.get(name)

    def select(self, deviceid: DeviceId):
        for dev in self.devices:
            if dev.deviceid == deviceid:
                return dev
