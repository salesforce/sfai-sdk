import sys

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points

from sfai.constants import WARNING_EMOJI


def get_integration_registry():
    registry = {}
    discovered_integrations = entry_points(group="sfai.integrations")
    for entry_point in discovered_integrations:
        try:
            integration_cls = entry_point.load()
            registry[entry_point.name] = integration_cls()
        except Exception as e:
            print(f"{WARNING_EMOJI} Error loading integration {entry_point.name}: {e}")
            continue
    return registry


INTEGRATION_REGISTRY = get_integration_registry()
