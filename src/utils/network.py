"""
Network utilities for ICS scanning and discovery.
"""
import asyncio
import socket
from typing import Optional, List, Tuple


def is_host_alive(ip: str, timeout: int = 2) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.gethostbyaddr(ip)
        return True
    except:
        return False


async def scan_port(ip: str, port: int, timeout: int = 2) -> Tuple[int, bool]:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        writer.close()
        return port, True
    except:
        return port, False


async def scan_ports(ip: str, ports: List[int], timeout: int = 2) -> List[int]:
    tasks = [scan_port(ip, p, timeout) for p in ports]
    results = await asyncio.gather(*tasks)
    return [port for port, is_open in results if is_open]


def ip_range_to_list(cidr: str) -> List[str]:
    import ipaddress
    return [str(ip) for ip in ipaddress.IPv4Network(cidr, strict=False)]


def mac_to_vendor(mac: str) -> Optional[str]:
    oui = mac[:8].upper().replace(":", "")
    vendors = {
        "00137A": "Siemens",
        "0000BC": "Rockwell",
        "0050C2": "Microchip",
        "0000F1": "Schneider",
        "0800DF": "ABB",
    }
    return vendors.get(oui, None)
