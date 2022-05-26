import time
import datetime
from typing import Optional

import model_pb2
from cancontroller.ipc.api import api
from cancontroller.caniot import *


class AlarmController(CustomPcb_Node):
    def __init__(self, deviceid: DeviceId, name: str = None):
        super().__init__(deviceid, name)

        self.model.update({
            "enabled": False,
            
            "triggered_count": 0,
            "last_signal": 0.0,

            "siren_count": 0,
            "last_siren": 0.0,

            "last_command": 0.0,
        })

    def get_model(self):
        return {
            "alarm": model_pb2.AlarmControllerModel(**self.model)
        }

    def handle_user_command(self, command) -> Command:
        print("Alarm : handle_user_command:", command)

        if command.alarm_state != 0:
            self.model.update({
                "enabled": True if command.alarm_state == 1 else 0,
            })

        return self.command(coc1=command.light1, coc2=command.light2,
                            crl1=XPS.SET_NONE if self.model['enabled'] else XPS.SET_OFF)

    def handle_board_control_telemetry(self, msg: CaniotMessage) -> Optional[CaniotMessage]:
        super(AlarmController, self).handle_board_control_telemetry(msg)

        print(self.model)

        cmd = None

        MIN_DELAY_BETWEEN_SIREN = 60 # 2min 30
        MIN_DELAY_BETWEEN_LIGHTS_COMMANDS = 5

        now = time.time()
        hour_of_day = datetime.datetime.now().hour

        if self.model['base']['in1']:  # if presence detected by sensor

            self.model['triggered_count'] += 1
            self.model['last_signal'] = now

            coc1 = XPS.SET_NONE
            coc2 = XPS.SET_NONE
            crl1 = XPS.SET_NONE

            if now - self.model['last_command'] > MIN_DELAY_BETWEEN_LIGHTS_COMMANDS:
                if hour_of_day in [19, 20, 21, 22, 23, 24, 0, 1, 2, 3, 4, 5]:
                    coc1 = XPS.PULSE_ON
                    coc2 = XPS.PULSE_ON

            if self.model['enabled'] and now - self.model['last_siren'] > MIN_DELAY_BETWEEN_SIREN:
                coc1 = XPS.PULSE_ON
                coc2 = XPS.PULSE_ON
                crl1 = XPS.PULSE_ON
                self.model['last_siren'] = now
                self.model['siren_count'] += 1

            if any([coc1, coc2, crl1]):
                cmd = BoardLevelCommand(self.deviceid, coc1=coc1,
                                        coc2=coc2, crl1=crl1)
                self.model['last_command'] = now
                print(BoardLevelCommand, cmd)

            return cmd
