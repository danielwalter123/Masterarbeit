import os
import json
import importlib
import actions
import information
import config

system = importlib.import_module("systems." + config.system)

if __name__ == "__main__":
    if hasattr(system, "init"):
        system.init()

    # Read json file
    steps = None
    base_path = os.path.dirname(os.path.abspath(__file__))
    steps_file = os.path.join(base_path, config.steps)
    with open(steps_file, 'r') as file:
        steps = json.load(file)

    if not steps or type(steps) is not list:
        exit()

    # Execute steps
    for step in steps:
        print("Next step: " + str(step))
        if "prerequisites" in step and isinstance(step["prerequisites"], list):
            for pr in step["prerequisites"]:
                information.handlers[pr["type"]].wait(pr["data"])
        actions.handlers[step["type"]].handle(step["data"])

    input("Press any key to exit... ")