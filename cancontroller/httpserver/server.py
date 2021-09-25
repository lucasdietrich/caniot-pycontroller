from __future__ import print_function

import jinja2
import aiohttp_jinja2
import grpc
import os.path

from aiohttp import web

from cancontroller import ROOT_DIR

from cancontroller.ipc import model_pb2
from cancontroller.ipc import model_pb2_grpc

from cancontroller import configuration
from cancontroller.controller.api import API
from cancontroller.caniot.devices import node_garage_door


# redirection
#            location = request.app.router['index'].url_for()
#            raise web.HTTPFound(location=location)

class HTTPServer(web.Application):
    def __init__(self, grpc_target: str):
        self.grpc_target = grpc_target

        self.api = API(grpc_target)

        super(HTTPServer, self).__init__()
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader('templates'))
        self.add_routes(
            [
                web.get('/garage', self.handle),
                web.post('/garage', self.handle),
                web.static("/static/", "./static"),

                web.get('/debug/{debug}', self.handle_debug),
                web.get("/", self.handle_home),
                web.get("/logs", self.handle_logs)
            ]
        )

        # context = request.query.get("context", "")
        #
        # print(context)

    @aiohttp_jinja2.template("home.view.j2")
    async def handle_home(self, request: web.Request):
        response = self.api.get_device_data(node_garage_door.deviceid)

        return {"model": response}

    @aiohttp_jinja2.template("garagedoor.view.j2")
    async def handle(self, request: web.Request):
        commands_list = [
            "Gauche",
            "Droite",
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
                      f"GarageResponse status={model_pb2._STATUS.values_by_number[response.status].name}")
            if form.get("debug", "") == "RequestTelemetry":
                self.api.RequestTelemetry(node_garage_door.deviceid)

        return {
            "device": self.api.get_device_data(node_garage_door.deviceid),
            "command": command,
            "commands_list": commands_list,
            "debug": bool(request.query.get("debug", ""))
        }


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