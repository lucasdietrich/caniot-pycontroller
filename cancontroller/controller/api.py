import grpc

import model_pb2
import model_pb2_grpc

from cancontroller.caniot.devices import DeviceId


class API:
    def __init__(self, grpc_target: str):
        self.grpc_target = grpc_target

    # https://github.com/kaporzhu/protobuf-to-dict
    def get_device_data(self, did: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)  # TODO stub initialized elsewhere
            return stub.GetDevice(model_pb2.DeviceId(type=did.data_type, id=did.sub_id))

    def RequestTelemetry(self, deviceid: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as  channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.RequestTelemetry(model_pb2.DeviceId(
                type=deviceid.data_type,
                id=deviceid.sub_id
            ))
