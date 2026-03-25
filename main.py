import os

import sentry_sdk
from dotenv import load_dotenv
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Envs
# LOAD FIRST!
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SENTRY_DSN = os.getenv("SENTRY_DSN")
AI_KEY = os.getenv("AI_KEY")
AI_API_URL = os.getenv("AI_API_URL")
AI_MODEL = os.getenv("AI_MODEL")


# OpenAI
smart_client = OpenAI(api_key=AI_KEY, base_url=AI_API_URL)
# Sentry
sentry_sdk.init(dsn=SENTRY_DSN, enable_logs=True)

app = App(token=SLACK_BOT_TOKEN)
