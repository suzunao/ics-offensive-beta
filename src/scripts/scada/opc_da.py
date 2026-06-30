def opc_read(target_ip: str, opc_server: str, tag: str):
    """Read a value from an OPC DA tag."""
    raise NotImplementedError


def opc_write(target_ip: str, opc_server: str, tag: str, value) -> bool:
    """Write a value to an OPC DA tag."""
    raise NotImplementedError


def opc_browse(target_ip: str, opc_server: str) -> list:
    """Browse all available tags on an OPC DA server."""
    raise NotImplementedError
