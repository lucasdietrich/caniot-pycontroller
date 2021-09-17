from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *

from enum import IntEnum, auto

# inherit grpc proto per Device type


class GarageDoorController(Device):
    class Door(IntEnum):
        NONE = 0
        LEFT = 1
        RIGHT = 2
        BOTH = 3

    def open_door(self, door: Door.BOTH) -> Command:
        return Command(self, [0, door], fit_buf=True)