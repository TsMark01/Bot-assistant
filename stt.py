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

def speech_to_text(data):
    """Transcribe audio to text using Yandex STT API."""
    params = "&".join([
        "topic=general",
        f"folderId={FOLDER_ID}",
        "lang=ru-RU"
    ])
    headers = {
        'Authorization': f'Bearer {IAM}',
    }
    try:
        response = requests.post(
            f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
            headers=headers,
            data=data
        )
        decoded_data = response.json()
        if decoded_data.get("error_code") is None:
            logging.info("STT: Successfully transcribed audio")
            return True, decoded_data.get("result")
        else:
            logging.error("STT: Failed to transcribe audio - API error")
            return False, "An error occurred while processing the audio in SpeechKit"
    except Exception as e:
        logging.error(f"STT: Error during transcription - {e}")
        return False, "An error occurred while processing the audio in SpeechKit"
