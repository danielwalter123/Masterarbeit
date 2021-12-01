from types import SimpleNamespace
import information
import importlib
import config
import time

system = importlib.import_module("systems." + config.system)

def handle(data):
    if data["type"] == "click":
        click(data["position"])

def click(position):
    if position["type"] == "information":
        info = position["data"]
        information.handlers[info["type"]].wait(info["data"])
        x, y = information.handlers[info["type"]].resolve_position(info["data"])
        time.sleep(0.5)
        print("Clicking on " + str(info["data"]))
        system.click(x, y)
    elif position["type"] == "coordinates":
        system.click(position["data"]["x"], position["data"]["y"])
