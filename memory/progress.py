import json
import os

SESSION_FILE = "memory/session.json"


def save_progress(current_topic_index, learning_path):
    data = {
        "current_topic_index": current_topic_index,
        "learning_path": learning_path
    }

    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_progress():
    if not os.path.exists(SESSION_FILE):
        return None

    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def clear_progress():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)