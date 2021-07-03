from __future__ import print_function

import jinja2
import aiohttp_jinja2
import grpc
from aiohttp import web

from cancontroller.ipc import model_pb2
from cancontroller.ipc import model_pb2_grpc


# redirection
#            location = request.app.router['index'].url_for()
#            raise web.HTTPFound(location=location)

class HTTPServer(web.Application):
    def __init__(self, grpc_target: str):
        self.grpc_target = grpc_target
        super(HTTPServer, self).__init__()
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader('templates'))
        self.add_routes([web.get('/garage', self.handle),
                        web.post('/garage', self.handle),
                        web.static("/garage/static", "./static"),
                        web.get('/debug/{debug}', self.handle_debug)])

    @aiohttp_jinja2.template("garagedoor.view.j2")
    async def handle(self, request: web.Request):
        commands_list = [
            "left",
            "right",
            "all",
        ]
        context = request.query.get("context", "")
        error = ""
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
            else:
                print("No command")
        return {
            "context": context,
            "error": error,
            "command": command,
            "commands_list": commands_list
        }

    async def handle_debug(self, request: web.Request):
        debug = request.match_info.get('debug', "")
        return web.Response(text=f"{debug}")


if __name__ == '__main__':
    app = HTTPServer(grpc_target='localhost:50051')
    web.run_app(app, host="0.0.0.0", port=8080)


# def run():
#     with grpc.insecure_channel('localhost:50051') as channel:
#         stub = model_pb2_grpc.CanControllerStub(channel)
#         response = stub.SendGarage(model_pb2.GarageCommand(datetime="128612936", command="OPENALL"))
#     print(f"CanController GarageResponse datetime={response.datetime} status={response.status}")
