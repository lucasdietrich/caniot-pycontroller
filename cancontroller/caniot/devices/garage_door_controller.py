from cancontroller.caniot.device import Device, Message

from enum import IntEnum, auto

# inherhit grpc proto per Device type


class GarageDoorController(Device):
    class Door(IntEnum):
        NONE = 0
        LEFT = 1
        RIGHT = 2
        BOTH = 3

    def open_door(self, door: Door.BOTH) -> Message:

        arbitration_id = MsgId(
            frame_type=MsgId.FrameType.Command,
            query_type=MsgId.QueryType.Query,
            controller=MsgId.Controller.BROADCAST,
            device_id=DeviceId(data_type=prodtype, sub_id=proddev)
        )
        return can.Message(arbitration_id=int(arbitration_id),
                           is_extended_id=False,
                           data=[0, relay, 0, 0]
                           )
