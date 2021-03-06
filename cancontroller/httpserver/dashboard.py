from aiohttp import web
import aiohttp_jinja2

from cancontroller.ipc.api import api
from cancontroller.controller.devices import node_alarm, node_broadcast, devices
from cancontroller.caniot.attributes import attributes
from cancontroller.caniot.datatypes import XPS

from cancontroller.utils import parse_number, number_to_hexn

from google.protobuf.json_format import MessageToJson

import datetime


async def context(request: web.Request):
    form = await request.post()

    # retrieving and parsing
    key = parse_number(form.get("key", "0x1010"))
    part = parse_number(form.get("part", "0"))
    wval = parse_number(form.get("wval", "0"))
    rval = None
    device_name = form.get("device", node_alarm.name)

    device = devices[device_name]
    if device is None:
        print(f"Device not found ! {device_name}")
    else:
        if form.get("telemetry"):
            ep_name = form.get("endpoint")
            eps = ["ep-0", "ep-1", "ep-2", "ep-3"]
            ep = eps.index(ep_name) if ep_name in eps else 0
            api.RequestTelemetry(device.deviceid, ep)
        elif form.get("read-attribute"):
            rval = api.ReadAttribute(device.deviceid, key + part)
        elif form.get("write-attribute"):
            rval = api.WriteAttribute(device.deviceid, key + part, wval)
        elif form.get("synctime"):
            api.SyncTime(node_broadcast.deviceid)
        elif form.get("oc1"):
            api.BoardLevelCommand(device.deviceid, coc1=XPS.TOGGLE)
        elif form.get("poc1"):
            api.BoardLevelCommand(device.deviceid, coc1=XPS.PULSE_ON)
        elif form.get("oc2"):
            api.BoardLevelCommand(device.deviceid, coc2=XPS.TOGGLE)
        elif form.get("poc2"):
            api.BoardLevelCommand(device.deviceid, coc2=XPS.PULSE_ON)
        elif form.get("rl1"):
            api.BoardLevelCommand(device.deviceid, crl1=XPS.TOGGLE)
        elif form.get("prl1"):
            api.BoardLevelCommand(device.deviceid, crl1=XPS.PULSE_ON)
        elif form.get("rl2"):
            api.BoardLevelCommand(device.deviceid, crl2=XPS.TOGGLE)
        elif form.get("prl2"):
            api.BoardLevelCommand(device.deviceid, crl2=XPS.PULSE_ON)

    # do this in a single grpc request !
    devlist = [
        (dev.name, dev.deviceid, dev.version, MessageToJson(api.GetDevice(dev.deviceid))) for dev in devices
    ]

    return {
        "devlist": devlist,
        "now": datetime.datetime.now().strftime('%A %d/%m/%Y %H:%M:%S'),
        "key": number_to_hexn(key, 4),
        "part": str(part),
        "rval": number_to_hexn(rval, 8) if rval is not None else "NONE",
        "wval": number_to_hexn(wval, 8) if wval > 0 else "",
        "irval": attributes.interpret(key + part, rval) if rval is not None else "",
        "attr": attributes.get_by_key(key + part),
        "selected_device": device_name,
        "attr_list": attributes.list
    }

@aiohttp_jinja2.template("dashboard.view.j2")
async def handle_get(request: web.Request):
    return await context(request)

@aiohttp_jinja2.template("dashboard.view.j2")
async def handle_post(request: web.Request):
    return await context(request)