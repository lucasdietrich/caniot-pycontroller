from cancontroller.caniot.models import MsgId, DeviceId
from cancontroller.caniot.device import Device

from cancontroller.caniot.devices.garage_door_controller import GarageDoorController

from typing import Dict, List, Union


class Devices:
    """
    List all devices on the current Bus
    """
    def __init__(self):
        self.list = {
            "GarageDoorControllerProdPCB": GarageDoorController(DeviceId(DeviceId.DataType.CRTAAA, 0))
        }

    def get(self, name: str):
        return self.list[name]

    def __getitem__(self, name: str):
        return self.get(name)

    def select(self, deviceid: DeviceId):
        for name, dev in self.list.items():
            if dev.deviceid == deviceid:
                return dev

