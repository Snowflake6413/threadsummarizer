import os

import sentry_sdk
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Envs
# LOAD FIRST!
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SENTRY_DSN = os.getenv("SENTRY_DSN")


# Sentry
sentry_sdk.init(dsn=SENTRY_DSN, enable_logs=True)

app = App(token=SLACK_BOT_TOKEN)
