import json
import os

#debug
class MemoryManager:

    def __init__(self, user_id):
        self.filename = f"memory/{user_id}.json"

    def load(self):
        if not os.path.exists(self.filename):
            return {}

        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            