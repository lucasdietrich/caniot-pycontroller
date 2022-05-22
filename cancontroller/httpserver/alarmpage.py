from aiohttp import web
import aiohttp_jinja2

from cancontroller.ipc.api import api
from cancontroller.controller.devices import node_alarm
from cancontroller.caniot.datatypes import XPS
from model_pb2 import COMMAND_ALARM_NONE, COMMAND_ALARM_ENABLE, COMMAND_ALARM_DISABLE

@aiohttp_jinja2.template("alarm.view.j2")
async def handle_get(request: web.Request):

    return {
        "device": api.GetDevice(node_alarm.deviceid)
    }

@aiohttp_jinja2.template("alarm.view.j2")
async def handle_post(request: web.Request):
    form = await request.post()

    print(form)

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

    both = form.get("both", "")
    if both in map:
        light1_cmd = map[both]
        light2_cmd = map[both]

    alarm_command = COMMAND_ALARM_NONE
    if form.get("enable-alarm", "") != "":
        alarm_command = COMMAND_ALARM_ENABLE
    elif form.get("disable-alarm", "") != "":
        alarm_command = COMMAND_ALARM_DISABLE

    if alarm_command or light1_cmd != XPS.SET_NONE or light2_cmd != XPS.SET_NONE:
        # api.BoardLevelCommand(node_alarm.deviceid, coc1=light1_cmd, coc2=light2_cmd)
        api.AlarmCommand(alarm_command, light1_cmd, light2_cmd)

    return {
        "device": api.GetDevice(node_alarm.deviceid)
    }