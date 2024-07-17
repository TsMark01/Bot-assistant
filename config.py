MAX_USERS = 8
MAX_GPT_TOKENS = 120
COUNT_LAST_MSG = 4

MAX_USER_STT_BLOCKS = 10
MAX_USER_TTS_SYMBOLS = 5000
MAX_USER_GPT_TOKENS = 4000

SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека. Также тебе будут доступны последние сообщения пользователя, чтобы ты мог понять как с ним общаться'}]  # список с системным промтом



LOGS = 'creds/logs.txt'
DB_FILE = 'hope.db'
TOKENIZE_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"
GPT_MODEL = 'yandexgpt-lite'
GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
