from cancontroller.caniot import *
from cancontroller.ipc.api import API
from cancontroller.ipc import model_pb2

import time
import datetime

api = API('192.168.10.155:50051')

api.BoardLevelCommand(node_alarm.deviceid, coc1=XPS.SET_ON)