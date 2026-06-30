def modbus_scan(target_ip: str, port: int = 502) -> dict:
    """Scan a Modbus device for accessible function codes and register ranges."""
    raise NotImplementedError


def modbus_broadcast(function_code: int, data: bytes) -> dict:
    """Send a Modbus broadcast message to all devices on the network."""
    raise NotImplementedError
