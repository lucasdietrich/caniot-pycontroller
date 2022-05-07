from cancontroller.caniot.models import DeviceId
from cancontroller.caniot.device import Device

from cancontroller.controller.nodes import GarageDoorController, AlarmController

node_garage_door = GarageDoorController(DeviceId(DeviceId.Class.CUSTOMPCB, 0x02), "GarageDoorControllerProdPCB")
node_alarm = AlarmController(DeviceId(DeviceId.Class.CUSTOMPCB, 0x03), "AlarmController")
node_broadcast = Device(DeviceId.Broadcast(), "__broadcast__")

# TODO create an entity of broadcast device


class Devices:
    """
    List all nodes on the current Bus
    """
    devices = [
        node_garage_door,
        node_alarm,
        node_broadcast
    ]

    def __iter__(self):
        for dev in self.devices:
            yield dev

    def get(self, name: str) -> Device:
        for dev in self.devices:
            if dev.name == name:
                return dev

    def __getitem__(self, name: str) -> Device:
        return self.get(name)

    def select(self, deviceid: DeviceId) -> Device:
        for dev in self.devices:
            if dev.deviceid == deviceid:
                return dev


devices = Devices()