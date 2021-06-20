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

@aiohttp_jinja2.template("garagedoor.view.j2")
async def handle(request: web.Request):
    commands_list = [
        "open-left",
        "close-left",
        "open-right",
        "close-right"
    ]
    context = request.query.get("context", "")
    error = ""
    command = ""

    if request.method == 'POST':
        form = await request.post()
        command = form.get("command", "")
        if command in commands_list:
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = model_pb2_grpc.CanControllerStub(channel)
                response = stub.SendGarage(model_pb2.GarageCommand(command=commands_list.index(command)))
            print(command)
            print(f"CanController GarageResponse datetime={response.datetime} status={response.status}")
        else:
            print("No command")
    return {
        "context": context,
        "error": error,
        "command": command,
        "commands_list": commands_list
    }


async def debug(request: web.Request):
    debug = request.match_info.get('debug', "")
    return web.Response(text=f"{debug}")


app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app.add_routes([web.get('/garage', handle),
                web.post('/garage', handle),
                web.static("/garage/static", "./static"),
                web.get('/debug/{debug}', debug)])


if __name__ == '__main__':
    web.run_app(app, host="0.0.0.0", port=8080)


# def run():
#     with grpc.insecure_channel('localhost:50051') as channel:
#         stub = model_pb2_grpc.CanControllerStub(channel)
#         response = stub.SendGarage(model_pb2.GarageCommand(datetime="128612936", command="OPENALL"))
#     print(f"CanController GarageResponse datetime={response.datetime} status={response.status}")