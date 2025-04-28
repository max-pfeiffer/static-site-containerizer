"""Test utilities."""

import platform


def get_platform() -> str:
    """Create Docker platform string.

    :return:
    """
    machine = platform.machine()
    match machine:
        case "x86_64":
            platform_value = "linux/amd64"
        case "arm64":
            platform_value = "linux/arm64"
        case _:
            platform_value = "linux/amd64"

    return platform_value
