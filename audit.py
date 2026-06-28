import json
import os

LOG_FILE = "logs/audit_log.json"


def save_log(entry):

    os.makedirs("logs", exist_ok=True)

    if os.path.exists(LOG_FILE):

        with open(LOG_FILE, "r") as file:
            logs = json.load(file)

    else:

        logs = []

    logs.append(entry)

    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)


def get_log():

    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as file:
        return json.load(file)
    
def overwrite_log(logs):

    with open(LOG_FILE, "w") as file:
        #json.dump(logs, file, indent=4)
        json.dump(logs, file, indent=4)