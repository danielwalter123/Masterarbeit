import json
import importlib
import actions
import information
import config
importlib.import_module("systems." + config.system)


# Read json file
steps = None
with open(config.steps, 'r') as file:
    steps = json.load(file)

if not steps or type(steps) is not list:
    exit()

# Execute steps
step = steps.pop(0)
while step:
    print("Next step: " + str(step))
    if "prerequisites" in step and isinstance(step["prerequisites"], list):
        for pr in step["prerequisites"]:
            information.handlers[pr["type"]].wait(pr["data"])
    actions.handlers[step["type"]].handle(step["data"])
    step = steps.pop(0) if len(steps) > 0 else None