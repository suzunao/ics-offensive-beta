def modbus_read(target_ip: str, port: int = 502, address: int = 0, count: int = 1, function_code: int = 3) -> list:
    """Read data from a Schneider Modicon PLC via Modbus."""
    raise NotImplementedError


def modbus_write(target_ip: str, address: int, value, function_code: int = 6) -> bool:
    """Write data to a Schneider Modicon PLC via Modbus."""
    raise NotImplementedError


def modbus_exception_fuzz(target_ip: str, port: int = 502, duration: int = 30) -> dict:
    """Fuzz a Schneider Modicon PLC with malformed Modbus exception responses."""
    raise NotImplementedError
