import secret.keys as keys
from src.gpt_function import gpt_function
import json
import requests

@gpt_function
def get_basic_info():
    """
    Useful for getting all the basic information - the current time, the current date, the current location.
    """