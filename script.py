"""
Text Gen Use API
Bypasses the generate reply and uses an external api. 

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
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

params = {
    "display_name": "Use External API",
    "is_tab": False,
    "api_reply": "",
}

def gen_from_api(string,model,state,type):
    print(os.environ["OPENAI_API_KEY"])
    print(state)
    if type == "OpenAI":
        response = requests.post("https://api.openai.com/v1/chat/completions",
            headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
            json={"model": model,
            "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": string}]})
        response_data = json.loads(response.content)
        params['api_reply'] = response_data["choices"][0]["message"]["content"]
        return 
    if type == "Anthropic":
        response = requests.post(
    "https://api.anthropic.com/v1/complete",
    headers={
        "accept": "application/json",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "x-api-key": os.environ["ANTHROPIC_API_KEY"]
    },
    json={
        "model": "claude-2.1",
        "prompt": "\n\nHuman: Hello, world!\n\nAssistant:",
        "max_tokens_to_sample": 256
    }
)
        return str(response.content)

    if type == "Cohere":
        response = requests.post(
    "https://api.cohere.ai/v1/chat",
    headers={
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {os.environ['COHERE_API_KEY']}"
    },
    json={
        "chat_history": [
            {"role": "USER", "message": "Who discovered gravity?"},
            {"role": "CHATBOT", "message": "The man who is widely credited with discovering gravity is Sir Isaac Newton"}
        ],
        "message": "What year was he born?",
        "connectors": [{"id": "web-search"}]
    }
)
        return str(response.content)
    if type == "Mistral":
        response = requests.post(
    "https://api.mistral.ai/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"
    },
    json={
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": "Who is the most renowned French writer?"}]
    }
)
        return str(response.content)
    if type == "Google":
        response = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + os.environ["GOOGLE_API_KEY"],
    headers={
        "Content-Type": "application/json"
    },
    json={
        "contents": [
            {
                "parts": [
                    {
                        "text": "Write a story about a magic backpack."
                    }
                ]
            }
        ]
    }
)
        return str(response.content)
    if type == "Custom":
        return str(response.content)
    pass



def input_modifier(string, state, is_chat=False):
    """
    In default/notebook modes, modifies the whole prompt.

    In chat mode, it is the same as chat_input_modifier but only applied
    to "text", here called "string", and not to "visible_text".
    """
    gen_from_api(string,"gpt-3.5-turbo",state,"OpenAI")
    
    return string


def output_modifier(string, state, is_chat=False):
    """
    Modifies the LLM output before it gets presented.

    In chat mode, the modified version goes into history['visible'],
    and the original version goes into history['internal'].
    """
    #print(string)
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
