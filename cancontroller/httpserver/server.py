from __future__ import print_function

import os.path

import aiohttp_jinja2
import grpc
import jinja2
from aiohttp import web

import dashboard
import alarmpage
from cancontroller import ROOT_DIR
from cancontroller import configuration
from cancontroller.controller.devices import node_garage_door, node_alarm
from cancontroller.ipc.api import api
import model_pb2, model_pb2_grpc
from cancontroller.caniot.models import DeviceId

from cancontroller import utils

# redirection
#            location = request.app.router['index'].url_for()
#            raise web.HTTPFound(location=location)


class HTTPServer(web.Application):
    def __init__(self, grpc_target: str):
        self.grpc_target = grpc_target

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

                web.get('/dashboard', dashboard.handle_get),
                web.post('/dashboard', dashboard.handle_post),

                web.get('/alarmcontroller', alarmpage.handle_get),
                web.post('/alarmcontroller', alarmpage.handle_post),

                web.static("/static/", "./static"),

                web.get('/debug/{debug}', self.handle_debug),
                web.get("/", self.handle_home),
                web.get("/logs", self.handle_logs),
                web.get("/caniot-temperatures", self.handle_temperatures),
                web.get("/metrics", self.handle_metrics)
            ]
        )

        # context = request.query.get("context", "")
        #
        # print(context)

    @aiohttp_jinja2.template("home.view.j2")
    async def handle_home(self, request: web.Request):
        response = api.GetDevice(node_garage_door.deviceid)

        return {"model": response}

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
            "device": api.GetDevice(node_garage_door.deviceid),
            "command": command,
            "commands_list": commands_list
        }

    async def handle_temperatures(self, request: web.Request):
        # TODO api.GetDevices()
        garage = api.GetDevice(node_garage_door.deviceid)
        alarm = api.GetDevice(node_alarm.deviceid)

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

    async def handle_metrics(self, request: web.Request):
        # TODO api.GetDevices()
        garage = api.GetDevice(node_garage_door.deviceid)
        alarm = api.GetDevice(node_alarm.deviceid)

        def build_device_temperature_metric(did: DeviceId, device_name: str, temp: float, embedded: bool = True) -> str:
            def build_tag(name: str, value: str) -> str:
                return f"{name}=\"{value}\""

            return "device_temperature{" + ",".join(
                build_tag(tag, val) for tag, val in {
                    "medium": "CAN",
                    "mac": str(int(did)),
                    "device": device_name,
                    "sensor": "EMBEDDED" if embedded else "EXTERNAL",
                    "room": "",
                    "collector": "pycaniotcontroller"
                }.items()
            ) + "} " + f"{temp:.2f}\n"

        metrics = ""

        if garage.garage.base.active_int_temp:
            metrics += build_device_temperature_metric(node_garage_door.deviceid, "GarageDoorController", garage.garage.base.int_temp, True)

        if alarm.alarm.base.active_int_temp:
            metrics += build_device_temperature_metric(node_alarm.deviceid, "AlarmController", alarm.alarm.base.int_temp, True)

        if alarm.alarm.base.active_ext_temp:
            metrics += build_device_temperature_metric(node_alarm.deviceid, "AlarmController", alarm.alarm.base.ext_temp, False)

        return web.Response(body=metrics)

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