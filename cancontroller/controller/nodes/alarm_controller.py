import time
from typing import Optional

import model_pb2
from cancontroller.ipc.api import api
from cancontroller.caniot import *


class AlarmController(CustomPcb_Node):
    def __init__(self, deviceid: DeviceId, name: str = None):
        super().__init__(deviceid, name)

        self.model.update({
            "enabled": True,
            "triggered_count": 0,
            "last_signal": 0.0
        })

    def get_model(self):
        return {
            "alarm": model_pb2.AlarmControllerModel(**self.model)
        }

    def handle_board_control_telemetry(self, msg: CaniotMessage) -> Optional[CaniotMessage]:
        super(AlarmController, self).handle_board_control_telemetry(msg)

        cmd = None

        if self.model['base']['in1']:
            now = time.time()

            if now - self.model['last_signal'] > 60.0:
                self.model['triggered_count'] += 1
                self.model['last_signal'] = now

                if self.model['enabled']:
                    api.BoardLevelCommand(self.deviceid, coc1=XPS.SET_ON,
                                          coc2=XPS.SET_ON, crl1=XPS.SET_NONE)

        return cmd