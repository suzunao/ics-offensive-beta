def start_modbus_c2(listen_port: int = 502, beacon_register: int = 1000, command_register: int = 1002) -> bool:
    """Start a Modbus-based C2 server that hides commands in register values."""
    raise NotImplementedError


def stop_modbus_c2() -> bool:
    """Stop the Modbus-based C2 server."""
    raise NotImplementedError
