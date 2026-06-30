"""
Modbus TCP protocol implementation for offensive operations.
"""
import asyncio
from typing import Optional, List, Tuple


class ModbusClient:
    def __init__(self, host: str, port: int = 502, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.transaction_id = 1

    async def _send_receive(self, unit_id: int, function_code: int, data: bytes) -> bytes:
        length = len(data) + 2
        header = bytes([
            self.transaction_id >> 8, self.transaction_id & 0xFF,
            0, 0, length >> 8, length & 0xFF,
            unit_id, function_code
        ])
        self.transaction_id += 1

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), timeout=self.timeout
        )
        writer.write(header + data)
        response = await asyncio.wait_for(reader.read(1024), timeout=self.timeout)
        writer.close()
        return response

    async def read_holding_registers(self, address: int, count: int = 1, unit_id: int = 1) -> List[int]:
        data = bytes([address >> 8, address & 0xFF, count >> 8, count & 0xFF])
        response = await self._send_receive(unit_id, 3, data)
        if len(response) < 9:
            return []
        byte_count = response[8]
        registers = []
        for i in range(byte_count // 2):
            idx = 9 + i * 2
            registers.append((response[idx] << 8) | response[idx + 1])
        return registers

    async def write_single_register(self, address: int, value: int, unit_id: int = 1) -> bool:
        data = bytes([address >> 8, address & 0xFF, value >> 8, value & 0xFF])
        response = await self._send_receive(unit_id, 6, data)
        return len(response) >= 12

    async def write_multiple_registers(self, address: int, values: List[int], unit_id: int = 1) -> bool:
        byte_count = len(values) * 2
        data = bytes([address >> 8, address & 0xFF, len(values) >> 8, len(values) & 0xFF, byte_count])
        for v in values:
            data += bytes([v >> 8, v & 0xFF])
        response = await self._send_receive(unit_id, 16, data)
        return len(response) >= 12

    async def read_coils(self, address: int, count: int = 1, unit_id: int = 1) -> List[bool]:
        data = bytes([address >> 8, address & 0xFF, count >> 8, count & 0xFF])
        response = await self._send_receive(unit_id, 1, data)
        if len(response) < 9:
            return []
        byte_count = response[8]
        coils = []
        for i in range(byte_count):
            byte = response[9 + i]
            for bit in range(8):
                if len(coils) < count:
                    coils.append(bool(byte & (1 << bit)))
        return coils

    async def write_single_coil(self, address: int, value: bool, unit_id: int = 1) -> bool:
        data = bytes([address >> 8, address & 0xFF, 0xFF if value else 0x00, 0x00])
        response = await self._send_receive(unit_id, 5, data)
        return len(response) >= 12

    async def exception_fuzz(self, duration: int = 30, unit_id: int = 1):
        import random
        end_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < end_time:
            fc = random.choice([1, 2, 3, 4, 5, 6, 15, 16, 17, 20, 21, 22, 23, 24])
            addr = random.randint(0, 0xFFFF)
            value = random.randint(0, 0xFFFF)
            try:
                if fc in [1, 2, 3, 4]:
                    await self._send_receive(unit_id, fc, bytes([addr >> 8, addr & 0xFF, 0, 1]))
                elif fc == 6:
                    await self.write_single_register(addr, value, unit_id)
                elif fc == 5:
                    await self.write_single_coil(addr, random.choice([True, False]), unit_id)
            except:
                pass
            await asyncio.sleep(0.01)
