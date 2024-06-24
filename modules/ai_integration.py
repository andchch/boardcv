import os
import requests

API = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

def ollama_check():
    models = requests.get('http://localhost:11434/api/tags').json()
    return models


def ollama_init():
    requests.post('http://localhost:11434/api/pull', json={'name': 'llama3'})
    

def ollama_sendmsg(msg: str, context):
    prompt = msg
    payload = {
        'model': 'llama3',
        'prompt': prompt,
        'context': context,
        'stream': False
    }
    response = requests.post('http://localhost:11434/api/generate', json=payload).json()
    
    return response['response']


def yagpt_sendmsg(msg: str, context, key):
    folder = 'b1gau53ip36hi7h6npao'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Api-Key {}'.format(key),
        'x-folder-id': folder,
        'x-data-logging-enabled': 'true'
    }
    payload = {
        "modelUri": f"gpt://{folder}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "1000"
        },
        "messages": [
        {
            "role": "system",
            "text": context
        },
        {
            "role": "user",
            "text": msg
        }
        ]
    }
    
    response = requests.post(API, json=payload, headers=headers).json()
    return response['result']['alternatives'][0]['message']['text']


def ask_gpt(msg, context):
    if os.getenv('USE_LOCAL') == 'True':
        print('local')
        r = ollama_sendmsg(msg, context)
    else:
        print('yandex')
        r = yagpt_sendmsg(msg, context, os.getenv('YANDEX_API_KEY'))
    
    return r
