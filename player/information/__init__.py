import pkgutil
import importlib

handlers =  {}
for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    handlers[module_name] = importlib.import_module("information." + module_name)
