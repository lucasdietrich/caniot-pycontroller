from aiohttp import web
import aiohttp_jinja2

from cancontroller.ipc.api import api
from cancontroller.controller.devices import node_alarm
from cancontroller.caniot.datatypes import XPS

@aiohttp_jinja2.template("alarm.view.j2")
async def handle_get(request: web.Request):

    return {
        "device": api.GetDevice(node_alarm.deviceid)
    }

@aiohttp_jinja2.template("alarm.view.j2")
async def handle_post(request: web.Request):
    form = await request.post()

    map = {
        "none": XPS.SET_NONE,
        "on": XPS.SET_ON,
        "off": XPS.SET_OFF,
        "toggle": XPS.TOGGLE,
    }

    light1_cmd = XPS.SET_NONE
    light1 = form.get("light1", "none")
    if light1 in map:
        light1_cmd = map[light1]

    light2_cmd = XPS.SET_NONE
    light2 = form.get("light2", "none")
    if light2 in map:
        light2_cmd = map[light2]

    api.BoardLevelCommand(node_alarm.deviceid, coc1=light1_cmd, coc2=light2_cmd)

    return {
        "device": api.GetDevice(node_alarm.deviceid)
    }