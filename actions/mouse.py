import information
import importlib
import config

system = importlib.import_module("systems." + config.system)

def handle(data):
    if data["type"] == "click":
        click(data["position"])

def click(position):
    if position["type"] == "information":
        info = position["data"]
        information.handlers[info["type"]].wait(info["data"])
        x, y = information.handlers[info["type"]].resolve_position(info["data"])
        system.click(x, y)
