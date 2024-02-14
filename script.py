"""
Text Gen Use API
Bypasses the generate reply and uses an external api. 
"""

import gradio as gr

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
import textwrap
from dotenv import load_dotenv
load_dotenv()

params = {
    "display_name": "Use External API",
    "is_tab": False,
    "api_reply": "",
    "api_type": "OpenAI",
    "custom_api_url_textbox": "http://127.0.0.1:8081",
    "api_model": "gpt-3.5-turbo",
    "logit_bias": None,
    "logprobs": False,
    "top_logprobs": None,
    "n": 1,
    "presence_penalty": 0,
    "response_format": None,
    "tools": None,
    "tool_choice": None

}

def gen_from_api(string,model,state,type):
    prompt = string
    system = str(state["context"]) + str(state["history"]["visible"])
    
    if type == "OpenAI":
        if state["seed"] == -1:
            seed = None
        else:
            seed = state["seed"]
        response = requests.post("https://api.openai.com/v1/chat/completions",
            headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
            json={"model": model,
            "frequency_penalty": state["frequency_penalty"],
            "logit_bias": params["logit_bias"],
            "logprobs": params["logprobs"],
            "top_logprobs": params["top_logprobs"],
            "max_tokens": state["max_new_tokens"],
            "n": params["n"],
            "presence_penalty": params["presence_penalty"],
            "response_format": params["response_format"],
            "seed": seed,
            "stop": state["custom_stopping_strings"],
            "stream": False,
            "temperature": state["temperature"],
            "top_p": state["top_p"],
            "tools": params["tools"],
            "tool_choice": params["tool_choice"],
            "user": state["name1"],

            "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}]})
        
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
        
        if state["seed"] == -1:
            seed = None
        else:
            seed = state["seed"]
        response = requests.post(params['custom_api_url_textbox'] + "/v1/chat/completions",
            headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["CUSTOM_API_KEY"]},
            json={"model": model,
            "frequency_penalty": state["frequency_penalty"],
            "logit_bias": params["logit_bias"],
            "logprobs": params["logprobs"],
            "top_logprobs": params["top_logprobs"],
            "max_tokens": state["max_new_tokens"],
            "n": params["n"],
            "presence_penalty": params["presence_penalty"],
            "response_format": params["response_format"],
            "seed": seed,
            "stop": state["custom_stopping_strings"],
            "stream": False,
            "temperature": state["temperature"],
            "top_p": state["top_p"],
            "tools": params["tools"],
            "tool_choice": params["tool_choice"],
            "user": state["name1"],

            "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}]})
        
        response_data = json.loads(response.content)
        
        params['api_reply'] = response_data["choices"][0]["message"]["content"]
        return 
        
        
    pass



def input_modifier(string, state, is_chat=False):
    """
    In default/notebook modes, modifies the whole prompt.

    In chat mode, it is the same as chat_input_modifier but only applied
    to "text", here called "string", and not to "visible_text".
    """
    shared.processing_message = "Connecting to external API" + str(params['api_type']) + "..."
    model = params["api_model"]
    gen_from_api(string,model,state,params["api_type"])
    
    return string


def output_modifier(string, state, is_chat=False):
    """
    Modifies the LLM output before it gets presented.

    In chat mode, the modified version goes into history['visible'],
    and the original version goes into history['internal'].
    """
    
    string = params['api_reply']
    params['api_reply'] = ""
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

    with gr.Accordion("Memoir+ v.001"):
        with gr.Row():
            gr.Markdown(textwrap.dedent("""
        - If you find this extension useful, <a href="https://www.buymeacoffee.com/brucepro">Buy Me a Coffee:Brucepro</a> or <a href="https://ko-fi.com/brucepro">Support me on Ko-fi</a>
        - For feedback or support, please raise an issue on https://github.com/brucepro/text_gen_use_api
        """))
        with gr.Accordion("Settings"):  
            with gr.Row():
                api_type_button = gr.Radio(
                    choices={"OpenAI": "OpenAI","Anthropic": "Anthropic","Cohere": "Cohere","Mistral": "Mistral","Google": "Google", "Custom (OpenAI compatible)": "Custom"},
                    label="Choose the type of api:",
                    value=params['api_type'],
                )
                api_type_button.change(lambda x: params.update({'api_type': x}), api_type_button, None)
            with gr.Row():
                api_model_textbox = gr.Textbox(show_label=True, label="Model:", value=params['api_model'], elem_id="api_model_textbox")
                api_model_textbox.change(lambda x: params.update({'api_model': x}), api_model_textbox, None)
                custom_api_url_textbox = gr.Textbox(show_label=True, label="Custom API url:", value=params['custom_api_url_textbox'], elem_id="api_customurl_textbox")
                custom_api_url_textbox.change(lambda x: params.update({'custom_api_url_textbox': x}), custom_api_url_textbox, None)
    pass
