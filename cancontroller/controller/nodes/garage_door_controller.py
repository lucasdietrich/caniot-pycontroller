import model_pb2
from cancontroller.caniot import *


class GarageDoorController(CustomPcb_Node):
    def __init__(self, deviceid: DeviceId, name: str = None):
        super().__init__(deviceid, name)

        self.model.update({
            "left": 1,
            "right": 1,
            "gate": 1,
        })

    def open_door(self, door) -> Command:
        params = dict()

        if door == model_pb2.COMMAND_LEFT or door == model_pb2.COMMAND_ALL:
            params["crl1"] = XPS.PULSE_ON

        if door == model_pb2.COMMAND_RIGHT or door == model_pb2.COMMAND_ALL:
            params["crl2"] = XPS.PULSE_ON

        return self.command(**params)

    def handle_board_control_telemetry(self, msg: CaniotMessage):
        super(GarageDoorController, self).handle_board_control_telemetry(msg)

        self.model["left"] = self.model["base"]["in3"]
        self.model["right"] = self.model["base"]["in4"]
        self.model["gate"] = self.model["base"]["in2"]

    def get_model(self):
        return {
            "garage": model_pb2.GarageDoorModel(**self.model)
        }