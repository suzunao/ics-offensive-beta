"""
Payload generation utilities for ICS exploits.
"""
from typing import Optional, List


def modbus_tcp_header(transaction_id: int = 1, unit_id: int = 1, length: int = 6) -> bytes:
    return bytes([
        transaction_id >> 8, transaction_id & 0xFF,
        0, 0,
        length >> 8, length & 0xFF,
        unit_id
    ])


def s7_iso_cotp(rack: int = 0, slot: int = 1) -> bytes:
    return bytes.fromhex(f"0300001611e00000000100c0010ac1020100c20201{rack:02x}{slot:02x}")


def dnp3_request_header() -> bytes:
    return bytes.fromhex("05640c00000000010000000000000000000000")


def iec104_apci(send_seq: int = 0, recv_seq: int = 0) -> bytes:
    return bytes([0x68, 0x0e, send_seq & 0xFF, (send_seq >> 8) & 0xFF, recv_seq & 0xFF, (recv_seq >> 8) & 0xFF])
