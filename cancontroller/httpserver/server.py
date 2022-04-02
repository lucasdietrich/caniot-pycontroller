from __future__ import print_function

import datetime
import os.path
import time

import json
import aiohttp_jinja2
import grpc
import jinja2
from aiohttp import web
from google.protobuf.json_format import MessageToJson

import dashboard
from cancontroller import ROOT_DIR
from cancontroller import configuration
from cancontroller.caniot.devices import node_garage_door, node_alarm, Devices
from cancontroller.ipc import model_pb2, model_pb2_grpc, API
from cancontroller.caniot.models import DeviceId

from cancontroller import utils

# redirection
#            location = request.app.router['index'].url_for()
#            raise web.HTTPFound(location=location)


class HTTPServer(web.Application):
    def __init__(self, grpc_target: str):
        self.grpc_target = grpc_target

        self.api = API(grpc_target)

        super(HTTPServer, self).__init__()

        # https://aiohttp-jinja2.readthedocs.io/en/stable/
        aiohttp_jinja2.setup(self,
                             loader=jinja2.FileSystemLoader('templates'),
                             filters={
                                 "diffseconds": utils.diffseconds,
                                 "fmttimestamp": utils.fmttimestamp
                             })

        self.add_routes(
            [
                web.get('/garage', self.handle_garagedoors),
                web.post('/garage', self.handle_garagedoors),

                web.get('/alarmcontroller', self.handle_alarm),
                web.post('/alarmcontroller', self.handle_alarm),

                web.get('/dashboard', dashboard.handle_get),
                web.post('/dashboard', dashboard.handle_post),

                web.static("/static/", "./static"),

                web.get('/debug/{debug}', self.handle_debug),
                web.get("/", self.handle_home),
                web.get("/logs", self.handle_logs),
                web.get("/caniot-temperatures", self.handle_temperatures)
            ]
        )

        # context = request.query.get("context", "")
        #
        # print(context)

    @aiohttp_jinja2.template("home.view.j2")
    async def handle_home(self, request: web.Request):
        response = self.api.GetDevice(node_garage_door.deviceid)

        return {"model": response}

    @aiohttp_jinja2.template("alarm.view.j2")
    async def handle_alarm(self, request: web.Request):
        if request.method == 'POST':
            form = await request.post()

            if form.get("debug", "") == "RequestTelemetry":
                self.api.RequestTelemetry(node_alarm.deviceid)
            else:
                light_cmd_list = ["", "on", "off", "toggle"]
                siren_cmd_list = light_cmd_list
                alarm_cmd_list = ["", "enable", "disable", "recover"]
                mode_cmd_list = ["", "normal", "silent"]

                def cmd_from_button(name, commands_list, default_value):
                    val = form.get(name, "")
                    if val in commands_list:
                        return commands_list.index(val)
                    return default_value

                both_lights = cmd_from_button("both", light_cmd_list, model_pb2.LIGHT_CMD_NONE)
                if both_lights == model_pb2.LIGHT_CMD_NONE:
                    light1 = cmd_from_button("light1", light_cmd_list, model_pb2.LIGHT_CMD_NONE)
                    light2 = cmd_from_button("light2", light_cmd_list, model_pb2.LIGHT_CMD_NONE)
                else:
                    light1 = light2 = both_lights

                alarm = cmd_from_button("alarm", alarm_cmd_list, model_pb2.ALARM_CMD_NONE)
                alarm_mode = cmd_from_button("mode", mode_cmd_list, model_pb2.ALARM_MODE_CMD_NONE)
                siren = cmd_from_button("siren", siren_cmd_list, model_pb2.ALARM_SIREN_CMD_NONE)

                command = model_pb2.AlarmControllerCommand(
                    light1=light1, light2=light2,
                    alarm=alarm, alarm_mode=alarm_mode, siren = siren
                )

                with grpc.insecure_channel(self.grpc_target) as channel:
                    stub = model_pb2_grpc.CanControllerStub(channel)  # TODO stub initialized elsewhere
                    response = stub.SendAlarm(command)

                print(f"CanController "
                      f"AlarmCommand command={command} "
                      f"CommandResponse status={model_pb2._STATUS.values_by_number[response.status].name} : {response}")

        alarm_status_messages = [("inactive", "désactivée"), ("observing", "activée"),
                                 ("sounding", "en alerte"), ("recovering", "en récupération")]
        siren_status_messages = [("inactive", "éteinte"), ("sounding", "activée")]

        device_data = self.api.GetDevice(node_alarm.deviceid)

        return {
            "device": device_data,
            "debug": bool(request.query.get("debug", "")),
            "alarm_status_message": alarm_status_messages[device_data.alarm.state],
            "siren_status_message": siren_status_messages[device_data.alarm.siren]
        }

    @aiohttp_jinja2.template("garagedoor.view.j2")
    async def handle_garagedoors(self, request: web.Request):
        commands_list = [
            "Gauche",
            "Droite",
            "<both>"
        ]
        command = ""
        if request.method == 'POST':
            form = await request.post()
            command = form.get("command", "")
            if command in commands_list:
                with grpc.insecure_channel(self.grpc_target) as channel:
                    stub = model_pb2_grpc.CanControllerStub(channel)  # TODO stub initialized elsewhere
                    response = stub.SendGarage(model_pb2.GarageCommand(command=commands_list.index(command) + 1))

                print(f"CanController "
                      f"GarageCommand command={command} "
                      f"CommandResponse status={model_pb2._STATUS.values_by_number[response.status].name}")

        return {
            "device": self.api.GetDevice(node_garage_door.deviceid),
            "command": command,
            "commands_list": commands_list
        }

    async def handle_temperatures(self, request: web.Request):
        # TODO self.api.GetDevices()
        garage = self.api.GetDevice(node_garage_door.deviceid)
        alarm = self.api.GetDevice(node_alarm.deviceid)

        def to_object(did, base):
            return {
                "deviceid": int(DeviceId(cls=did.cls, sid=did.sid)),
                "active_int_temp": bool(base.active_int_temp),
                "int_temp": f"{base.int_temp:.2f}",
                "active_ext_temp": bool(base.active_ext_temp),
                "ext_temp": f"{base.ext_temp:.2f}",
            }

        return web.json_response([
            to_object(garage.deviceid, garage.garage.base),
            to_object(alarm.deviceid, alarm.alarm.base)
        ])

    async def handle_debug(self, request: web.Request):
        debug = request.match_info.get('debug', "")
        return web.Response(text=f"{debug}")

    # https://docs.aiohttp.org/en/stable/multipart.html
    async def handle_logs(self, request: web.Request):
        log_file = os.path.join(ROOT_DIR, configuration.get_controller_log_file())

        if os.path.exists(log_file):
            # if request.query.get("clear", "") == "1":
            #     os.lseek()
            #     return web.Response(status=200)

            return web.FileResponse(log_file, headers={
                "Content-Disposition": 'attachment; filename="logs.txt"'
            })
        else:
            return web.Response(
                status=404
            )


if __name__ == '__main__':
    app = HTTPServer(grpc_target=f'localhost:{configuration.grpc_port}')
    web.run_app(app, host="0.0.0.0", port=configuration.http_server_port)