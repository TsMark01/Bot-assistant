# User and Token Limits
MAX_USERS = 8  # Maximum number of unique users allowed to interact with the bot
MAX_GPT_TOKENS = 120  # Maximum tokens for a single GPT response
COUNT_LAST_MSG = 4  # Number of previous messages to include for GPT context
MAX_USER_STT_BLOCKS = 10  # Maximum speech-to-text blocks per user
MAX_USER_TTS_SYMBOLS = 5000  # Maximum text-to-speech symbols per user
MAX_USER_GPT_TOKENS = 4000  # Maximum GPT tokens per user

# System Prompt for Yandex GPT
SYSTEM_PROMPT = [{
    'role': 'system',
    'text': 'You are a fun and friendly conversationalist. Chat with the user informally, using humor, and keep the dialogue engaging. Act like a human and don’t mention your capabilities. Use the user’s recent messages to tailor your responses.'
}]  # System prompt for GPT behavior

# File Paths
LOGS = 'creds/logs.txt'  # Path to the log file for debugging
DB_FILE = 'hope.db'  # Path to the SQLite database file

# Yandex API Configuration
TOKENIZE_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion'  # URL for tokenizing GPT input
GPT_MODEL = 'yandexgpt-lite'  # Yandex GPT model used
GPT_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'  # URL for GPT completion
