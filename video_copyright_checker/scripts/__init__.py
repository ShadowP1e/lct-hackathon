import logging
import importlib.util
import sys

def load_config(config_path):
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config
    spec.loader.exec_module(config)
    return config

settings = load_config('settings.py')

logging.basicConfig(filename='database.log', level=logging.DEBUG)
