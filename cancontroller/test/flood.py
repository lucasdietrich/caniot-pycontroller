from time import sleep

from cancontroller.ipc.api import api, DeviceId


while True:
    api.RequestTelemetry(DeviceId(DeviceId.Class.CUSTOMPCB, 3))
    # sleep(0.150)