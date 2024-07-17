import telebot
from telebot import types
from telebot.types import Message
import logging
from config import *
from database import add_message, create_database, select_n_last_messages
from tokens import check_number_of_users, is_gpt_token_limit, is_stt_block_limit, is_tts_symbol_limit
from yandex_gpt import ask_gpt
from tts import text_to_speech
from stt import speech_to_text
from secret import *


logging.basicConfig(filename=LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="a")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message(message.from_user.id, '"Я помощник который может общаться с вами и Аудио и текстовыми сообщениями, задайте мне вопрос в удобном формате. Напишите /help для помощи по командам"')


@bot.message_handler(commands=['feedback'])
def feedback_handler(msg: Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    item3 = types.KeyboardButton("Неудовлетворительный ответ от нейросети")
    item2 = types.KeyboardButton("Не работают команды")
    item1 = types.KeyboardButton('Все отлично, мне понравилось!')

    markup.add(item1, item2, item3)

    bot.send_message(msg.chat.id, 'Оставьте отзыв, если вам не сложно!(можете просто написать сообщение с отзывом '
                                  'или воспользоваться вариантами под строкой ввода)'.format(msg.from_user,
                                                                                             bot.get_me()),
                     reply_markup=markup,
                     parse_mode='html')

    bot.register_next_step_handler(msg, feedback)


def feedback(msg: Message):
    with open('creds/feedback.txt', 'a', encoding='utf-8') as f:
        f.write(f'{msg.from_user.first_name}({msg.from_user.id}) оставил отзыв - "{msg.text}"\n')
        bot.send_message(msg.chat.id, 'Спасибо за отзыв!')


@bot.message_handler(commands=['help'])
def help_user(message: Message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст\n"
                                           "команды:\n"
                                           "/start - запуск бота\n"
                                           "/help - помощь\n"
                                           "/feedback - обратная связь\n"
                                           "Можете просто отправлять вопросы и бот ответит вам как нейросеть."
                     )


@bot.message_handler(commands=['debug'])
def debug(message: Message):
    try:
        with open(LOGS, "rb") as f:
            bot.send_document(message.chat.id, f)
    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(message.chat.id, 'Не получилось отправить файл с логами. Попробуйте позже.')
        logging.error(e)


@bot.message_handler(content_types=['voice'])
def handle_voice(message: Message):
    user_id = message.from_user.id
    try:
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)

        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)

        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")


@bot.message_handler(commands=['stt', 'start'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt)


def stt(message: Message):
    user_id = message.from_user.id

    if not message.voice:
        return

    success, stt_blocks = is_stt_block_limit(user_id, message.voice.duration)

    if not success:
        bot.send_message(user_id, stt_blocks)
        return

    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)

    status, text = speech_to_text(file)

    add_message(user_id, [text, 'assistant', 0, 0, stt_blocks])

    if status:
        bot.send_message(user_id, text, reply_to_message_id=message.id)

    else:
        bot.send_message(user_id, text)


@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщеним текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)


def tts(message: Message):
    user_id = message.from_user.id
    text = message.text

    if message.content_type != 'text':
        bot.send_message(user_id, 'Отправь текстовое сообщение')
        return

    tts_symbol, error_message = is_tts_symbol_limit(user_id, text)

    if error_message:
        bot.send_message(user_id, error_message)
        return

    status, content = text_to_speech(text)

    add_message(user_id, [text, 'user', 0, tts_symbol, 0])

    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)


@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    user_id = message.from_user.id
    try:
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)

        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, 'Не получилось ответить.'
                                          'Обратитесь в другой раз')



logging.info('programm start')
create_database()
bot.polling()