import time
import grpc
from typing import Union

from cancontroller.caniot import *

import model_pb2, model_pb2_grpc


# Diagnostic
# Controller aprameters, speed, ..
# Device last seen, message, stats, database
# reqest telemetry


class API:
    def __init__(self, grpc_target: str = '192.168.10.155:50051'):
        self.grpc_target = grpc_target

    def ReadAttribute(self, deviceid: DeviceId, key: int, timeout: float = 1.0) -> int:
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            response = stub.ReadAttribute(model_pb2.AttributeRequest(
                device=model_pb2.DeviceId(
                    cls=deviceid.cls,
                    sid=deviceid.sid
                ),
                key=key,
                timeout=timeout
            ))
            # print(model_pb2._STATUS.values_by_number[response.status].name, response.value)
            return response.value if response.status == model_pb2.OK else None

    def WriteAttribute(self, deviceid: DeviceId, key: int, value: int, timeout: float = 1.0) -> int:
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            response = stub.WriteAttribute(model_pb2.AttributeRequest(
                device=model_pb2.DeviceId(
                    cls=deviceid.cls,
                    sid=deviceid.sid
                ),
                key=key,
                value=value,
                timeout=timeout
            ))
            return response.value if response.status == model_pb2.OK else None

    def SyncTime(self, deviceid: DeviceId, synctime: int = 0):
        if not synctime:
            synctime = int(time.time())

        return self.WriteAttribute(deviceid, attributes.get("time").key, synctime)

    def GetDevice(self, deviceid: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.GetDevice(model_pb2.DeviceId(
                cls=deviceid.cls,
                sid=deviceid.sid
            ))

    def GetDevices(self):
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            response = stub.WriteAttribute(model_pb2.Empty())
            return response

    def RequestTelemetry(self, deviceid: DeviceId, endpoint: model_pb2.TELEMETRY_ENDPOINT):
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.RequestTelemetry(model_pb2.TelemetryTarget(
                deviceid=model_pb2.DeviceId(
                    cls=deviceid.cls,
                    sid=deviceid.sid),
                endpoint=endpoint
            ))

    def Reset(self, deviceid: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.Reset(model_pb2.DeviceId(
                cls=deviceid.cls,
                sid=deviceid.sid
            ))

    def BoardLevelCommand(self, deviceid: DeviceId, coc1=XPS.SET_NONE, coc2=XPS.SET_NONE,
                          crl1=XPS.SET_NONE, crl2=XPS.SET_NONE):
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.CommandDevice(model_pb2.BoardLevelCommand(
                device=model_pb2.DeviceId(cls=deviceid.cls, sid=deviceid.sid),
                coc1=coc1,
                coc2=coc2,
                crl1=crl1,
                crl2=crl2
            ))


api = API('192.168.10.155:50051')

if __name__ == "__main__":
    did = DeviceId(DeviceId.Class.CUSTOMPCB, 0x03)
    response_read_attr = api.ReadAttribute(did, 0x1010)
    print(response_read_attr)
