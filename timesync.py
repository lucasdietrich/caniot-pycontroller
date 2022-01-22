from cancontroller.caniot import *
from cancontroller.ipc.api import API
from cancontroller.ipc import model_pb2

import time
import datetime

api = API('192.168.10.155:50051')

avr_can_tool_commands = {
    "alarm_read_time": "can tx 0xc3 10 10"
}


device_time = api.ReadAttribute(node_alarm.deviceid, attributes.get("time").key)
if device_time is None:
    print("Failed to get a value from the device")
    exit()

real_time = int(time.time())
diff = device_time - real_time

print(f"Current device time : {device_time} sec")
print(f"Real time is : {real_time} sec")

print(f"- Error is {diff} sec")

if abs(diff) > 10:
    print("Updating device time")
    api.WriteAttribute(DeviceId.Broadcast(), attributes.get("time").key, int(time.time()))

