from dotenv import load_dotenv
from .loader import merge_config

load_dotenv()

def get_config(args):
    return merge_config(args)
