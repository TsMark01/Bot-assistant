import requests
import logging
from config import LOGS
from secret import IAM, FOLDER_ID


logging.basicConfig(filename=LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="a")


def text_to_speech(text):
    headers = {
        'Authorization': f'Bearer {IAM}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'filipp',
        'folderId': FOLDER_ID
    }
    response = requests.post(
        'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        return True, response.content
    else:
        return False, response
