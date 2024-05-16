import requests

#TODO: Use LangChain
#TODO: Write GPU start documentation and nvidia container toolkit installation
#      nvidia: https://github.com/ollama/ollama/blob/main/docs/docker.md#nvidia-gpu
def ollama_check():
    models = requests.get('http://localhost:11434/api/tags').json()
    return models


def ollama_init():
    requests.post('http://localhost:11434/api/pull', json={'name': 'llama3'})
    

def ollama_sendmsg(msg: str):
    prompt = msg
    payload = {
        'model': 'llama3',
        'prompt': prompt,
        'stream': False
    }
    response = requests.post('http://localhost:11434/api/generate', json=payload).json()
    
    return response['response']
