"""
Text_gen use api. 
Accepts a compatible api and ignores generation using the backend. Allows you to just 
use the frontend and other extensions with text gen and an api server. 
"""

import gradio as gr
import torch
from transformers import LogitsProcessor

from modules import chat, shared
from modules.text_generation import (
    decode,
    encode,
    generate_reply,
)
import sys, os
import requests
import json
import time 
from pathlib import Path
from datetime import datetime
import random
from requests.auth import HTTPBasicAuth
import base64

params = {
    "display_name": "Example Extension",
    "is_tab": False,
    "api_reply": "",
}


def gen_from_api(string):
    AIurl = f"http://127.0.0.1:8080/completion"
    starttime = time.time()
    req_json = {
    "stream": False,
    "n_predict": 24576,
    "temperature": 0.7,
    "stop": [
        "</s>",
    ],
    "repeat_last_n": 256,
    "repeat_penalty": 1,
    "top_k": 20,
    "top_p": 0.75,
    "tfs_z": 1,
    "typical_p": 1,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "mirostat": 0,
    "mirostat_tau": 5,
    "mirostat_eta": 0.1,
    "grammar": "",
    "n_probs": 0,
    "prompt": string
    }

    print(string)
    res = requests.post(AIurl, json=req_json)
    result = res.json()["content"]   
    endtime = time.time()
    runtime = endtime - starttime
    print(f"Runtime: {runtime}s")
    print(result)
    return result


def input_modifier(string, state, is_chat=False):
    """
    In default/notebook modes, modifies the whole prompt.

    In chat mode, it is the same as chat_input_modifier but only applied
    to "text", here called "string", and not to "visible_text".
    """
    params['api_reply'] = gen_from_api(string)
    return string


def output_modifier(string, state, is_chat=False):
    """
    Modifies the LLM output before it gets presented.

    In chat mode, the modified version goes into history['visible'],
    and the original version goes into history['internal'].
    """
    print(string)
    string = params['api_reply']
    return string


def setup():
    """
    Gets executed only once, when the extension is imported.
    """
    pass

def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.

    To learn about gradio components, check out the docs:
    https://gradio.app/docs/
    """
    pass
