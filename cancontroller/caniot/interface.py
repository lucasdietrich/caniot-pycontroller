import os

DEFAULT_BITRATE = 500000 # 500KBPS
DEFAULT_TXQUEUELEN = 65536


def initialize_can_if(can_if: str, bitrate: int = DEFAULT_BITRATE, txqueuelen: int = DEFAULT_TXQUEUELEN):
    ret = os.system(f"sudo ip link show {can_if}")

    os.system(f"sudo ip link set {can_if} down")
    
    os.system(f"sudo ip link set {can_if} up type can bitrate {bitrate}")

    os.system(f"sudo ifconfig can0 txqueuelen {txqueuelen}")