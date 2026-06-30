"""
IEC 60870-5-104 protocol implementation for RTU/breaker operations.
"""
import asyncio
from typing import Optional, List, Dict


class IEC104Client:
    def __init__(self, host: str, port: int = 2404, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.send_seq = 0
        self.recv_seq = 0

    async def connect(self) -> bool:
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), timeout=self.timeout
            )
            return True
        except:
            return False

    async def _send(self, data: bytes) -> bytes:
        if not hasattr(self, 'writer'):
            await self.connect()
        self.writer.write(data)
        return await asyncio.wait_for(self.reader.read(1024), timeout=self.timeout)

    async def single_command(self, ioa: int, command: str = "ON") -> bytes:
        cmd_val = 0x01 if command == "ON" else 0x00
        asdu = bytes([
            0x68, 0x0e, 0x00, 0x00, 0x00, 0x00,
            0x2d, 0x01, 0x03, 0x00, 0x01, 0x00,
            ioa & 0xFF, (ioa >> 8) & 0xFF, (ioa >> 16) & 0xFF,
            0x81, 0x00, cmd_val, 0x00
        ])
        return await self._send(asdu)

    async def interrogation(self) -> bytes:
        asdu = bytes.fromhex("68140000000000640106000001000000")
        return await self._send(asdu)

    async def close(self):
        if hasattr(self, 'writer'):
            self.writer.close()
