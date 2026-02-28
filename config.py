import os

# Assistant Configuration
ASSISTANT_NAME = "Mona"
WAKE_WORD = "mona"
STOP_WORD = "stop"

# User Configuration
USER_NAME = "Sir"
USER_EMAIL = "your_email@example.com"  # Replace with actual email
USER_PHONE = "+910000000000"          # Replace with actual phone

# Telegram Configuration (For Phone Integration)
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE" 
AUTHORIZED_USER_ID = None  # Set this to your Telegram ID to prevent others from controlling

# Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

INTERACTIONS_LOG = os.path.join(LOGS_DIR, "interactions.txt")
