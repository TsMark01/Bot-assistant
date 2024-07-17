import json
import requests
import logging
from config import LOGS, MAX_GPT_TOKENS, SYSTEM_PROMPT, TOKENIZE_URL, GPT_MODEL, GPT_URL
from secret import *

logging.basicConfig(filename=LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="a")


def count_gpt_tokens(messages):
    headers = {
        'Authorization': f'Bearer {IAM}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "messages": messages
    }
    try:
        response = requests.post(url=TOKENIZE_URL, json=data, headers=headers).json()['tokens']
        return len(response)
    except Exception as e:
        logging.error(e)
        return 0


def ask_gpt(messages):
    headers = {
        'Authorization': f'Bearer {IAM}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{FOLDER_ID}/{GPT_MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": MAX_GPT_TOKENS
        },
        "messages": SYSTEM_PROMPT + messages
    }
    try:
        response = requests.post(GPT_URL, headers=headers, json=data)
        if response.status_code != 200:
            return False, f"Ошибка GPT. Статус-код: {response.status_code}", None
        answer = response.json()['result']['alternatives'][0]['message']['text']
        tokens_in_answer = count_gpt_tokens([{'role': 'assistant', 'text': answer}])
        return True, answer, tokens_in_answer
    except Exception as e:
        logging.error(e)
        return False, "Ошибка при обращении к GPT",  None


if __name__ == '__main__':
    print(count_gpt_tokens([{'role': 'user', 'text': 'Привет'}]))
