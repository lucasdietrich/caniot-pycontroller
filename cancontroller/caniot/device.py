import can

from cancontroller.caniot import DeviceId, MsgId
from can import Message


class Device:
    """
    Represent a caniot device on the can bus.

    Gather all device specific methods
    """

    def __init__(self, deviceid: DeviceId):
        self.deviceid = deviceid

    def __repr__(self):
        return f"Device {self.deviceid}"

    def query(self, buffer: list) -> Message:

        MsgId.Command(self.deviceid, )
        arbitration_id = MsgId(
            frame_type=MsgId.FrameType.Command,
            query_type=MsgId.QueryType.Query,
            controller=MsgId.Controller.BROADCAST,
            device_id=DeviceId(data_type=prodtype, sub_id=proddev)
        )

        return can.Message(arbitration_id=int(arbitration_id),
                           is_extended_id=False,
                           data=buffer
                           )

    def read_attribute(self, attr) -> Message:
        pass

