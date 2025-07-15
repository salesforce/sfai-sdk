import sys

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points

from sfai.core.base import BasePlatform
from sfai.constants import WARNING_EMOJI


def get_platform_registry():
    registry = {}
    discovered_platforms = entry_points(group="sfai.platforms")
    for entry_point in discovered_platforms:
        try:
            platform_cls = entry_point.load()
            if not issubclass(platform_cls, BasePlatform):
                print(
                    f"{WARNING_EMOJI} Platform {entry_point.name} must "
                    f"inherit from BasePlatform"
                )
                continue
            registry[entry_point.name] = platform_cls()
        except Exception as e:
            print(f"{WARNING_EMOJI} Error loading platform {entry_point.name}: {e}")
            continue
    return registry


PLATFORM_REGISTRY = get_platform_registry()
