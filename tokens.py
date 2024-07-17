import logging
import math
from config import *
from database import count_users, count_all_limits
from yandex_gpt import count_gpt_tokens


logging.basicConfig(filename=LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="a")


def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return None, "Ошибка при работе с БД"
    if count > MAX_USERS:
        return None, "Превышено максимальное количество пользователей"
    return True, ""


def is_gpt_token_limit(messages, total_spent_tokens):
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
    return all_tokens, ""


def is_stt_block_limit(user_id, duration):
    audio_blocks = math.ceil(duration / 15)
    all_blocks = count_all_limits(user_id, 'stt_blocks') + audio_blocks

    if duration >= 30:
        response = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        return None, response

    if all_blocks >= MAX_USER_STT_BLOCKS:
        response = (f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. "
                    f"Доступно: "f"{MAX_USER_STT_BLOCKS - all_blocks}")
        return None, response

    return audio_blocks, None


def is_tts_symbol_limit(user_id, text):
    text_symbols = len(text)

    all_symbols = count_all_limits(user_id, 'tts_symbols') + text_symbols

    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = (f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. "
               f"Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}")
        return None, msg

    return text_symbols, None
