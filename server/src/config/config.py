import json

def load_config():
    with open("./src/config/config.json", "r") as f:
        data = json.load(f)
        try:
            return data
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")

config = load_config()