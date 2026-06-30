def class0_read(target_ip: str, port: int = 20000) -> list:
    """Perform a DNP3 Class 0 (all data) read against an RTU."""
    raise NotImplementedError


def class123_read(target_ip: str, port: int = 20000) -> dict:
    """Perform DNP3 Class 1/2/3 reads against an RTU for event data."""
    raise NotImplementedError
