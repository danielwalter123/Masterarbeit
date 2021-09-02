import importlib
import config

system = importlib.import_module("systems." + config.system)

def handle(data):
    if data["type"] == "text":
        system.text(data["text"])

