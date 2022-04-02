import struct

U10_MAX_VALUE = 0x3ff

def IntHum2float(H: int) -> float:
    return (H & U10_MAX_VALUE) / 100.0

def IntPres2float(P: int) -> float:
    return (P & U10_MAX_VALUE) / 100.0 + 950.0


def IntTemp2float(T: int) -> float:
    return (T & U10_MAX_VALUE) / 10.0 - 28.0

def Temperature2float(raw: bytes) -> float:
    T = struct.unpack("h", raw)[0]
    return IntTemp2float(T)

def IsActiveT10(A: int):
    return A != U10_MAX_VALUE