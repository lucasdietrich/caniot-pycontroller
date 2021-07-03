from cancontroller.can import MsgId, DeviceId

from typing import Dict, List, Union

KNOWN_DEVICES: Dict[str, DeviceId] = {
    "garagedoor_dev": DeviceId(DeviceId.DataType.CRT, 0),
    "garagedoor_prod": DeviceId(DeviceId.DataType.CRT, 1)
}