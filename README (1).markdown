# Telegram Bot Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-4.x-orange.svg)](https://pypi.org/project/pyTelegramBotAPI/)

## 📋 Project Overview

This is my final project from the Yandex Course, completed in May 2024. The **Telegram Bot Assistant** is an interactive bot that communicates with users via text and voice messages. It uses Yandex GPT for generating responses, Speech-to-Text (STT) for transcribing voice inputs, and Text-to-Speech (TTS) for voice replies. The bot tracks usage limits (e.g., tokens, symbols, blocks) per user, stores conversation history in a SQLite database, and includes features like feedback and debugging. This project demonstrates skills in bot development, API integration, database management, and limit enforcement, making it a strong addition to my CS portfolio for UK university applications.

### 🎯 Key Objectives
- Handle text and voice interactions with users.
- Integrate Yandex APIs for GPT, STT, and TTS.
- Enforce user limits to prevent overuse.
- Log activities and store messages in a database for context-aware responses.
- Provide commands for help, feedback, and debugging.

## 🛠️ Tech Stack

| Category          | Tools/Technologies                  | Purpose |
|-------------------|-------------------------------------|---------|
| **Bot Framework** | pyTelegramBotAPI                   | Telegram bot handling |
| **AI Integration**| Yandex GPT, STT, TTS               | Response generation, voice processing |
| **Database**      | SQLite                             | Message history and limits tracking |
| **HTTP Requests** | Requests library                   | API calls to Yandex services |
| **Language**      | Python 3.9+                        | Core scripting |
| **Logging**       | Python logging                     | Error and activity tracking |
| **Version Control**| Git/GitHub                        | Code management |

## 🏗️ Architecture

The bot follows a modular design:

1. **User Input**: Handles text or voice via Telegram commands and handlers.
2. **Processing**:
   - Voice: STT converts to text, checks limits.
   - Text: Directly processes.
3. **GPT Response**: Fetches last messages from DB, sends to Yandex GPT with system prompt.
4. **Output**: Sends text response or TTS voice, updates DB with usage.
5. **Limits & Logging**: Checks user counts, tokens, symbols; logs all actions.

Key Files:
- `bot.py`: Main bot logic and handlers.
- `config.py`: Constants and system prompt.
- `database.py`: SQLite functions.
- `secret.py`: API tokens (keep secure, not committed).
- `stt.py`, `tts.py`, `yandex_gpt.py`: Yandex API integrations.
- `tokens.py`: Limit checking functions.
- `creds/logs.txt`: Log file.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Telegram Bot Token (from @BotFather)
- Yandex Cloud credentials (IAM token, Folder ID)
- Install dependencies: `pip install -r requirements.txt`

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/TsMark01/Bot-assistant.git
   cd Bot-assistant
   ```

2. **Configure Secrets**
   - Edit `secret.py` with your `IAM`, `FOLDER_ID`, and `TOKEN`.
   - Ensure `creds/` directory exists for logs.

3. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the Bot**
   ```bash
   python bot.py
   ```
   The bot will start polling. Interact via Telegram by sending text or voice messages.

### Usage Commands
- `/start`: Launch the bot and get a welcome message.
- `/help`: Display available commands.
- `/feedback`: Leave feedback (options or custom text).
- `/debug`: Send log file (for admins).
- `/stt`: Transcribe a voice message.
- `/tts`: Convert text to voice.

## 📊 Features

- **Voice & Text Support**: Seamless handling of both input types.
- **Context-Aware Responses**: Uses last 4 messages for GPT context.
- **Usage Limits**: Per-user caps on users (8), GPT tokens (4000), STT blocks (10), TTS symbols (5000).
- **Feedback System**: Saves user reviews to `creds/feedback.txt`.
- **Logging**: Detailed logs in `creds/logs.txt`.
- **System Prompt**: Bot acts as a fun, humorous companion.

## 🧪 Testing & Debugging

- Test interactions via Telegram.
- Check logs for errors: `cat creds/logs.txt`.
- Use `/debug` to retrieve logs.
- Database: Messages stored in `hope.db` for review.

## 🔮 Future Enhancements

- Add more advanced GPT models or integrations (e.g., OpenAI).
- Implement user authentication or roles.
- Deploy to a server (e.g., Heroku) for 24/7 availability.
- Enhance error handling and user notifications.

## 📝 Contributing

Fork the repo and submit PRs for improvements!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built by TsMark01 as Final Yandex Course Project (May 2024) | [Portfolio](https://github.com/TsMark01)*