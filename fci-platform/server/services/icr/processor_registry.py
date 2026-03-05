"""
Processor auto-discovery.
Scans the processors package for all BaseProcessor subclasses
and provides them sorted by display order.
"""

import importlib
import pkgutil


def discover_processors():
    """
    Find all BaseProcessor subclasses in the processors package.
    Returns a list of instantiated processors, sorted by sort_order.
    """
    from .processors.base import BaseProcessor

    package = importlib.import_module('.processors', package=__package__)
    processors = []

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name == 'base':
            continue
        module = importlib.import_module(
            f'.processors.{module_name}', package=__package__
        )
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseProcessor)
                and attr is not BaseProcessor
            ):
                processors.append(attr())

    return sorted(processors, key=lambda p: p.sort_order)


def get_processors_for_data(processors, available_file_types, params):
    """
    Filter processors to only those that have enough data to run.

    Args:
        processors: List of all discovered processor instances
        available_file_types: Set of file type keys present in the session
        params: Dict of manual form parameters

    Returns:
        List of processors that should run
    """
    return [p for p in processors if p.should_run(available_file_types, params)]