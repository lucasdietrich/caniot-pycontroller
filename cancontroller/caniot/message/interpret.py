from cancontroller.caniot.message import TelemetryMessage, AttributeResponse, Response, AttributeResponse

from cancontroller.caniot.models import MsgId, BufferType


def interpret_response(msgid: MsgId, buffer: BufferType):
    if msgid.is_response():
        if msgid.frame_type == MsgId.FrameType.ReadAttribute or msgid.frame_type == MsgId.FrameType.WriteAttribute:
            return AttributeResponse(msgid, buffer)
        elif msgid.frame_type == MsgId.FrameType.Telemetry:
            return TelemetryMessage(msgid, buffer)
        else:
            return Response(msgid, buffer)
    else:
        print(f"Msg isn't response : {int(msgid)} !")