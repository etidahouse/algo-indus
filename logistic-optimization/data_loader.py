import json
from config import DATA_PATH

def load_data(path=DATA_PATH):
    with open(path, "r") as fp:
        return json.load(fp)
