def enumerate_tags(target_ip: str, path: str = "") -> list:
    """Enumerate all tags from an Allen-Bradley ControlLogix/CompactLogix PLC using CIP."""
    raise NotImplementedError


def write_tag(target_ip: str, tag_name: str, value) -> bool:
    """Write a value to a specific tag on an Allen-Bradley PLC."""
    raise NotImplementedError


def change_controller_mode(target_ip: str, mode: str) -> bool:
    """Change the controller mode (RUN/PROG) of an Allen-Bradley PLC."""
    raise NotImplementedError
