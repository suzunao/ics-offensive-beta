"""
DNP3 protocol implementation for RTU operations.
"""
import asyncio
from typing import Optional, List, Dict, Any


class DNP3Client:
    def __init__(self, host: str, port: int = 20000, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout

    async def _send_receive(self, data: bytes) -> bytes:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), timeout=self.timeout
        )
        writer.write(data)
        response = await asyncio.wait_for(reader.read(4096), timeout=self.timeout)
        writer.close()
        return response

    async def class0_read(self) -> bytes:
        request = bytes.fromhex("05640c00000000010000000000000000000000")
        return await self._send_receive(request)

    async def class1_read(self) -> bytes:
        request = bytes.fromhex("05640c00010000010000000000000000000000")
        return await self._send_receive(request)

    async def class2_read(self) -> bytes:
        request = bytes.fromhex("05640c00020000010000000000000000000000")
        return await self._send_receive(request)

    async def class3_read(self) -> bytes:
        request = bytes.fromhex("05640c00030000010000000000000000000000")
        return await self._send_receive(request)

    async def crob_operate(self, index: int, control_code: int = 0x03, count: int = 1, on_time: int = 100, off_time: int = 100) -> bytes:
        request = bytes([0x05, 0x64, 0x0C, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00])
        crob = bytes([control_code, count & 0xFF, (count >> 8) & 0xFF, on_time & 0xFF, (on_time >> 8) & 0xFF, off_time & 0xFF, (off_time >> 8) & 0xFF])
        index_bytes = bytes([index & 0xFF, (index >> 8) & 0xFF])
        return await self._send_receive(request + crob + index_bytes)

    async def time_sync(self, offset_hours: int = 0) -> bytes:
        request = bytes.fromhex("05640c00000000010000000000000000000000")
        return await self._send_receive(request)

    async def unsolicited_response(self, event_type: str = "binary", values: list = None) -> bytes:
        if values is None:
            values = []
        request = bytes.fromhex("05640c00000000010000000000000000000000")
        return await self._send_receive(request)
