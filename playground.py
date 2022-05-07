from cancontroller.caniot import *
from cancontroller.ipc.api import api
import model_pb2
from cancontroller.controller.devices import node_alarm, node_broadcast


api.BoardLevelCommand(node_alarm.deviceid, coc1=XPS.SET_ON)