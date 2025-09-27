import requests
import logging
from config import LOGS
from secret import IAM, FOLDER_ID

logging.basicConfig(
    filename=LOGS,
    level=logging.DEBUG,
    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
    filemode="a"
)

def text_to_speech(text):
    """Convert text to speech using Yandex TTS API."""
    headers = {
        'Authorization': f'Bearer {IAM}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'filipp',
        'folderId': FOLDER_ID
    }
    try:
        response = requests.post(
            'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
            headers=headers,
            data=data
        )
        if response.status_code == 200:
            logging.info("TTS: Successfully synthesized speech")
            return True, response.content
        else:
            logging.error(f"TTS: Failed with status code {response.status_code}")
            return False, response
    except Exception as e:
        logging.error(f"TTS: Error during synthesis - {e}")
        return False, str(e)
