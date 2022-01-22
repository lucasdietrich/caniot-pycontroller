from cancontroller.caniot.models import MsgId, DeviceId
from cancontroller.caniot.device import Device

from cancontroller.caniot.nodes.garage_door_controller import GarageDoorController
from cancontroller.caniot.nodes.alarm_controller import AlarmController

from typing import Dict, List, Union, Optional

node_garage_door = GarageDoorController(DeviceId(DeviceId.Class.CRTHPT, 0x02), "GarageDoorControllerProdPCB")
node_alarm = AlarmController(DeviceId(DeviceId.Class.CRTHPT, 0x03), "AlarmController")

# TODO create an entity of broadcast device


class Devices:
    """
    List all nodes on the current Bus
    """
    devices = [
        node_garage_door,
        node_alarm
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