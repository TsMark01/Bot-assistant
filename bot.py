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

logging.basicConfig(
    filename=LOGS,
    level=logging.DEBUG,
    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
    filemode="a"
)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message: Message):
    """Send a welcome message to the user."""
    bot.send_message(
        message.from_user.id,
        "I'm an assistant that can communicate via audio or text messages. Ask me a question in your preferred format. Use /help for command details."
    )

@bot.message_handler(commands=['feedback'])
def feedback_handler(message: Message):
    """Prompt the user to provide feedback with a reply keyboard."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton("Everything is great, I love it!")
    item2 = types.KeyboardButton("Commands are not working")
    item3 = types.KeyboardButton("Unsatisfactory response from the AI")
    markup.add(item1, item2, item3)

    bot.send_message(
        message.chat.id,
        "Please leave your feedback if you don't mind! You can write a custom message or use the options below.",
        reply_markup=markup,
        parse_mode='html'
    )
    bot.register_next_step_handler(message, feedback)

def feedback(message: Message):
    """Save user feedback to a file and thank the user."""
    with open('creds/feedback.txt', 'a', encoding='utf-8') as f:
        f.write(f"{message.from_user.first_name}({message.from_user.id}) submitted feedback - \"{message.text}\"\n")
    bot.send_message(message.chat.id, "Thank you for your feedback!")
    logging.info(f"Feedback received from {message.from_user.id}: {message.text}")

@bot.message_handler(commands=['help'])
def help_user(message: Message):
    """Display available commands and usage instructions."""
    bot.send_message(
        message.from_user.id,
        "To start interacting, send a voice or text message.\n"
        "Commands:\n"
        "/start - Launch the bot\n"
        "/help - Show this help message\n"
        "/feedback - Provide feedback\n"
        "/stt - Transcribe a voice message\n"
        "/tts - Convert text to voice\n"
        "You can also send questions directly, and I'll respond using AI."
    )

@bot.message_handler(commands=['debug'])
def debug(message: Message):
    """Send the log file to the user if accessible."""
    try:
        with open(LOGS, "rb") as f:
            bot.send_document(message.chat.id, f)
        logging.info(f"Log file sent to user {message.from_user.id}")
    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(message.chat.id, "Failed to send the log file. Please try again later.")
        logging.error(f"Error sending log file: {e}")

@bot.message_handler(content_types=['voice'])
def handle_voice(message: Message):
    """Process voice messages, transcribe, and respond using GPT."""
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
        logging.info(f"Voice message transcribed for user {user_id}: {stt_text}")

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
            logging.info(f"Voice response sent to user {user_id}")
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
            logging.info(f"Text response sent to user {user_id}: {answer_gpt}")

    except Exception as e:
        logging.error(f"Error processing voice message: {e}")
        bot.send_message(user_id, "Sorry, I couldn't respond. Please try another message.")

@bot.message_handler(commands=['stt'])
def stt_handler(message: Message):
    """Prompt the user to send a voice message for transcription."""
    user_id = message.from_user.id
    bot.send_message(user_id, "Send a voice message, and I'll transcribe it!")
    bot.register_next_step_handler(message, stt)

def stt(message: Message):
    """Transcribe a voice message and store it."""
    user_id = message.from_user.id
    if not message.voice:
        bot.send_message(user_id, "Please send a voice message.")
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
        logging.info(f"Transcription successful for user {user_id}: {text}")
    else:
        bot.send_message(user_id, text)
        logging.error(f"Transcription failed for user {user_id}: {text}")

@bot.message_handler(commands=['tts'])
def tts_handler(message: Message):
    """Prompt the user to send text for voice conversion."""
    user_id = message.from_user.id
    bot.send_message(user_id, "Send the text you want me to convert to voice!")
    bot.register_next_step_handler(message, tts)

def tts(message: Message):
    """Convert text to voice and send it to the user."""
    user_id = message.from_user.id
    text = message.text

    if message.content_type != 'text':
        bot.send_message(user_id, "Please send a text message.")
        return

    tts_symbols, error_message = is_tts_symbol_limit(user_id, text)
    if error_message:
        bot.send_message(user_id, error_message)
        return

    status, content = text_to_speech(text)
    add_message(user_id, [text, 'user', 0, tts_symbols, 0])

    if status:
        bot.send_voice(user_id, content)
        logging.info(f"Text-to-speech successful for user {user_id}")
    else:
        bot.send_message(user_id, content)
        logging.error(f"Text-to-speech failed for user {user_id}: {content}")

@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    """Process text messages and respond using GPT."""
    user_id = message.from_user.id
    try:
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)
        logging.info(f"Text message received from user {user_id}: {message.text}")

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
        logging.info(f"GPT response sent to user {user_id}: {answer_gpt}")

    except Exception as e:
        logging.error(f"Error processing text message: {e}")
        bot.send_message(message.chat.id, "Sorry, I couldn't respond. Please try again later.")

logging.info('Bot started')
create_database()
bot.polling()
