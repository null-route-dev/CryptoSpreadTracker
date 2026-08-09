from dotenv import load_dotenv
from .config_loader import merge_config

load_dotenv()

def get_config(args):
    config = merge_config(args)
    return config
