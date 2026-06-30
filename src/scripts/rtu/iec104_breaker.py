def single_command(target_ip: str, port: int = 2404, ioa: int = 0, command: str = "ON") -> bool:
    """Send a single IEC 60870-5-104 command to control a breaker or switch."""
    raise NotImplementedError


def mass_trip(targets: list, delay_ms: int = 10) -> dict:
    """Send simultaneous IEC 104 commands to trip multiple breakers."""
    raise NotImplementedError


def interrogation(target_ip: str, port: int = 2404) -> list:
    """Perform an IEC 104 general interrogation to enumerate all points."""
    raise NotImplementedError
