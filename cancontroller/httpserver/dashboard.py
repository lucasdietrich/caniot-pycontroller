from aiohttp import web
import jinja2
import aiohttp_jinja2

from cancontroller.ipc import model_pb2, model_pb2_grpc, API
from cancontroller import configuration
from cancontroller.caniot.devices import node_garage_door, node_alarm, node_broadcast, devices

from cancontroller.utils import parse_number, number_to_hexn

from google.protobuf.json_format import MessageToJson

import datetime

api = API()


async def context(request: web.Request):
    form = await request.post()

    # retrieving and parsing
    rkey = parse_number(form.get("rkey", "0x1010"))
    wkey = parse_number(form.get("wkey", "0x1010"))
    wval = parse_number(form.get("wval", "0"))
    rval = None
    device_name = form.get("device", node_broadcast.name)

    device = devices[device_name]
    if device is None:
        print(f"Device not found ! {device_name}")
    else:
        if form.get("telemetry"):
            res = api.RequestTelemetry(device.deviceid)
        elif form.get("read-attribute"):
            rval = api.ReadAttribute(device.deviceid, rkey)
        elif form.get("write-attribute"):
            rval = api.WriteAttribute(device.deviceid, wkey, wval)
        elif form.get("synctime"):
            api.SyncTime(device.deviceid)

    # do this in a single grpc request !
    devlist = [
        (dev.name, dev.deviceid, dev.version, MessageToJson(api.GetDevice(dev.deviceid))) for dev in devices
    ]

    return {
        "devlist": devlist,
        "now": datetime.datetime.now().strftime('%A %d/%m/%Y %H:%M:%S'),
        "rkey": number_to_hexn(rkey, 4),
        "rval": number_to_hexn(rval, 8) if rval is not None else "NONE",
        "wkey": number_to_hexn(wkey, 4),
        "wval": number_to_hexn(wval, 8),
        "selected_device": device_name
    }

@aiohttp_jinja2.template("dashboard.view.j2")
async def handle_get(request: web.Request):
    return await context(request)

@aiohttp_jinja2.template("dashboard.view.j2")
async def handle_post(request: web.Request):
    return await context(request)