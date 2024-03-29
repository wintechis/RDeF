import importlib
import pkgutil
import sys


def import_submodules(package_name):
    # copied from https://stackoverflow.com/questions/3365740/how-to-import-all-submodules
    """Import all submodules of a module, recursively

    :param package_name: Package name
    :type package_name: str
    :rtype: dict[types.ModuleType]
    """
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + "." + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    }


__all__ = import_submodules(__name__).keys()
