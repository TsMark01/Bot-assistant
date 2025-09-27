import requests
import logging
from config import LOGS, MAX_GPT_TOKENS, SYSTEM_PROMPT, TOKENIZE_URL, GPT_MODEL, GPT_URL
from secret import IAM, FOLDER_ID

logging.basicConfig(
    filename=LOGS,
    level=logging.DEBUG,
    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
    filemode="a"
)

def count_gpt_tokens(messages):
    """Count tokens in messages using Yandex GPT tokenize API."""
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
        logging.info(f"GPT: Tokenized {len(response)} tokens for messages")
        return len(response)
    except Exception as e:
        logging.error(f"GPT: Error tokenizing messages - {e}")
        return 0

def ask_gpt(messages):
    """Generate a response using Yandex GPT API."""
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
            logging.error(f"GPT: Failed with status code {response.status_code}")
            return False, f"GPT error. Status code: {response.status_code}", None
        answer = response.json()['result']['alternatives'][0]['message']['text']
        tokens_in_answer = count_gpt_tokens([{'role': 'assistant', 'text': answer}])
        logging.info(f"GPT: Generated response with {tokens_in_answer} tokens")
        return True, answer, tokens_in_answer
    except Exception as e:
        logging.error(f"GPT: Error generating response - {e}")
        return False, "Error communicating with GPT", None

if __name__ == '__main__':
    print(count_gpt_tokens([{'role': 'user', 'text': 'Hello'}]))
