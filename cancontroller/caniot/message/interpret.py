from cancontroller.caniot.message import TelemetryMessage, AttributeResponse, AttributeResponse, CaniotMessage

from cancontroller.caniot.models import MsgId, BufferType


def interpret_response(msgid: MsgId, buffer: BufferType):
    if msgid.is_response():
        if msgid.frame_type == MsgId.FrameType.ReadAttribute:
            return AttributeResponse(msgid, buffer)
        elif msgid.frame_type == MsgId.FrameType.Telemetry:
            return TelemetryMessage(msgid, buffer)
        else:
            return CaniotMessage(msgid, buffer)
    else:
        return CaniotMessage(msgid, buffer)