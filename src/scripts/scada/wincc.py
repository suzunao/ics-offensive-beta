def connect_default_sql(target_ip: str, use_default_creds: bool = True) -> dict:
    """Connect to Siemens WinCC using default SQL Server credentials."""
    raise NotImplementedError


def opc_da_write(target_ip: str, opc_server: str, tag: str, value) -> bool:
    """Write a value to an OPC DA tag on a WinCC server."""
    raise NotImplementedError
