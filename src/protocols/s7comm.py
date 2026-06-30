"""
S7comm (S7 Communication) protocol implementation for Siemens PLC operations.
"""
import asyncio
from typing import Optional, List, Dict, Any


class S7Client:
    def __init__(self, host: str, port: int = 102, rack: int = 0, slot: int = 1, timeout: int = 5):
        self.host = host
        self.port = port
        self.rack = rack
        self.slot = slot
        self.timeout = timeout
        self.pdu_ref = 1

    async def connect(self) -> bool:
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), timeout=self.timeout
            )
            # ISO connect
            iso_cotp = bytes.fromhex("0300001611e00000000100c0010ac1020100c20201" +
                                     f"{self.rack:02x}{self.slot:02x}")
            self.writer.write(iso_cotp)
            resp = await asyncio.wait_for(self.reader.read(1024), timeout=self.timeout)
            return len(resp) > 0
        except:
            return False

    async def _send_pdu(self, pdu: bytes) -> bytes:
        if not hasattr(self, 'writer'):
            await self.connect()
        self.writer.write(pdu)
        return await asyncio.wait_for(self.reader.read(8192), timeout=self.timeout)

    async def extract_block(self, block_type: str, block_number: int) -> bytes:
        pdu = bytes.fromhex("030000" + "".join(f"{b:02x}" for b in [0x21, 0xe0, 0x00, 0x00, 0x00, 0x2f, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        return await self._send_pdu(pdu)

    async def extract_all_blocks(self) -> List[Dict[str, Any]]:
        blocks = []
        for bt in ["OB", "FB", "FC", "DB"]:
            for bn in range(1, 100):
                try:
                    data = await self.extract_block(bt, bn)
                    if len(data) > 50:
                        blocks.append({"type": bt, "number": bn, "size": len(data)})
                except:
                    pass
        return blocks

    async def stop(self) -> bool:
        pdu = bytes.fromhex("0300002111e0000000010001c0010a10000200000000000009h00h00" +
                            f"{self.rack:02x}{self.slot:02x}")
        resp = await self._send_pdu(pdu)
        return len(resp) > 0

    async def hot_restart(self) -> bool:
        pdu = bytes.fromhex("0300002511e0000000010001c0010a10000200000000000009" +
                            f"{self.rack:02x}{self.slot:02x}00h00h00h00h000000000000")
        resp = await self._send_pdu(pdu)
        return len(resp) > 0

    async def close(self):
        if hasattr(self, 'writer'):
            self.writer.close()
