"""
Cryptographic utilities for ICS credential handling.
"""
from typing import Optional, Dict, Any
import hashlib
import base64


def xor_decrypt(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])


def wonderware_decrypt(encrypted_data: str) -> str:
    key = b"\x00\x01\x02\x03\x04\x05\x06\x07"
    raw = bytes.fromhex(encrypted_data)
    decrypted = xor_decrypt(raw, key)
    return decrypted.rstrip(b"\x00").decode("utf-8", errors="ignore")


def s7_password_hash(password: str) -> str:
    return hashlib.sha1(password.encode()).hexdigest()[:16]


def rockwell_hash(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def base64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode()


def base64_decode(data: str) -> bytes:
    return base64.b64decode(data)
