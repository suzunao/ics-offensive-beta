"""
Target Analyzer — Escanea y perfila dispositivos OT/ICS.
Detecta vendor, modelo, protocolos, versión de firmware.
"""
import asyncio
import socket
from typing import Optional

class TargetAnalyzer:
    ICS_PORTS = {
        102: "S7comm (Siemens)",
        502: "Modbus TCP",
        20000: "DNP3",
        2404: "IEC 60870-5-104",
        44818: "EtherNet/IP (Allen-Bradley)",
        4840: "OPC UA",
        8088: "Ignition Gateway",
        2222: "CIP",
        2455: "IEC 61850 MMS",
    }

    async def probe_port(self, ip: str, port: int) -> dict:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), timeout=3
            )
            result = {"port": port, "open": True}

            if port in [102]:
                writer.write(bytes.fromhex("0300001611e00000000100c0010ac1020100c2020101"))
                data = await asyncio.wait_for(reader.read(1024), timeout=2)
                result["banner"] = data.hex()
                result["protocol"] = "S7comm"
                if len(data) > 20:
                    result["vendor"] = "Siemens"
            elif port == 502:
                writer.write(bytes.fromhex("000100000006010400000001"))
                data = await asyncio.wait_for(reader.read(1024), timeout=2)
                result["banner"] = data.hex()
                result["protocol"] = "Modbus TCP"
            elif port == 20000:
                writer.write(bytes.fromhex("0564"))
                data = await asyncio.wait_for(reader.read(1024), timeout=2)
                result["banner"] = data.hex()
                result["protocol"] = "DNP3"
            elif port == 44818:
                writer.write(bytes.fromhex("6500040000000000000000000000000000000000000000000000000000000000"))
                data = await asyncio.wait_for(reader.read(1024), timeout=2)
                result["banner"] = data.hex()
                result["protocol"] = "EtherNet/IP"

            writer.close()
            return result
        except:
            return {"port": port, "open": False}

    async def analyze(self, target_ip: str, ports: str = "102,502,20000,44818,2404,4840,8088") -> dict:
        port_list = [int(p.strip()) for p in ports.split(",")]

        tasks = [self.probe_port(target_ip, p) for p in port_list]
        results = await asyncio.gather(*tasks)

        open_services = [r for r in results if r.get("open")]

        profile = {
            "ip": target_ip,
            "open_services": open_services,
            "inferred_vendor": self._infer_vendor(open_services),
            "inferred_type": self._infer_device_type(open_services),
            "attack_surface": self._assess_attack_surface(open_services),
        }

        return profile

    def _infer_vendor(self, services: list) -> Optional[str]:
        protocols = [s.get("protocol", "") for s in services]
        banner_indicators = [s.get("banner", "") for s in services]

        if "S7comm" in protocols:
            return "Siemens"
        if "EtherNet/IP" in protocols or "CIP" in protocols:
            return "Rockwell/Allen-Bradley"
        if "Modbus TCP" in protocols:
            return "Generic Modbus (possibly Schneider)"
        if "DNP3" in protocols:
            return "Multiple (DNP3-capable RTU)"
        if "IEC 60870-5-104" in protocols:
            return "Multiple (IEC 104-capable)"

        return None

    def _infer_device_type(self, services: list) -> str:
        proto_set = {s.get("protocol") for s in services}

        if "S7comm" in proto_set:
            return "PLC"
        if "EtherNet/IP" in proto_set or "CIP" in proto_set:
            return "PLC"
        if "DNP3" in proto_set:
            return "RTU"
        if "IEC 60870-5-104" in proto_set:
            return "RTU"
        if "OPC UA" in proto_set:
            return "SCADA/Historian"
        if "Ignition Gateway" in proto_set:
            return "SCADA"

        return "Unknown OT Device"

    def _assess_attack_surface(self, services: list) -> list:
        surface = []
        for s in services:
            port = s.get("port")
            proto = s.get("protocol")
            if port == 102:
                surface.extend([
                    "plc_s7_extract",
                    "plc_s7_inject",
                    "plc_s7_password_crack",
                    "plc_s7_dos",
                ])
            elif port == 502:
                surface.extend([
                    "plc_modbus_read",
                    "plc_modbus_write",
                    "plc_modbus_fuzz",
                ])
            elif port == 20000:
                surface.extend([
                    "rtu_dnp3_crob",
                    "rtu_dnp3_recon",
                    "rtu_dnp3_time_sync",
                ])
            elif port == 2404:
                surface.extend([
                    "rtu_iec104_breaker",
                    "rtu_iec104_mass_trip",
                ])
            elif port == 44818:
                surface.extend([
                    "plc_cip_tag_enum",
                    "plc_cip_tag_write",
                    "plc_cip_mode_change",
                ])
        return surface
