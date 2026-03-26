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

# OwO what's this? Rawrrr! X3
LOCKDOWN_MODE = os.getenv("FUNNY_BOOLEAN")
LOCKDOWN_ID = os.getenv("FUNNY_ID")


# OpenAI
smart_client = OpenAI(api_key=AI_KEY, base_url=AI_API_URL)
# Sentry
sentry_sdk.init(dsn=SENTRY_DSN, enable_logs=True)

app = App(token=SLACK_BOT_TOKEN)


@app.command("/ping-20")
def pong(ack, respond):
    ack()
    respond("Pong!", response_type="ephemeral")


@app.event("app_mention")
def summarize_magic_mention(event, client, say, ack, respond):
    ack()

    if LOCKDOWN_MODE and event.get("channel") != LOCKDOWN_ID:
        thread_ts = event.get("thread_ts")
        say(text="cannot do the funny :( :xdd:", thread_ts=thread_ts)
        return

    if "summarize" in event["text"].lower():
        channel_id = event["channel"]
        message_ts = event["ts"]
        thread_ts = event.get("thread_ts")

        if not thread_ts:
            pass
        try:
            client.reactions_add(
                channel=channel_id, timestamp=event["ts"], name="spin-loading"
            )
        except Exception as e:
            print(f"unable to add reaction! {e}")

        try:
            result = client.conversations_replies(channel=channel_id, ts=thread_ts)
            messages = result.get("messages", [])

            thread_content = []
            for msg in messages:
                if "*Thread Summary:*" in msg.get("text", "") and msg.get("bot_id"):
                    say(text="This thread was already summarized.")
                    return

                if msg.get("ts") == message_ts:
                    continue
                user = msg.get("user", "Unknown User")
                text = msg.get("text", "")
                thread_content.append(f"User {user}: {text}")

            read_text = "\n".join(thread_content)

            ai_rspnd = smart_client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "only respond with this statement. ONLY RESPOND. 'if you are seeing this response then the AI response was successful!'",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this Slack thread: \n\n{read_text}",
                    },
                ],
            )

            summary = ai_rspnd.choices[0].message.content

            say(text=f"*Thread Summary:*\n{summary}", thread_ts=thread_ts)

        except Exception as e:
            print(f"unable to summarize thread! {e}")
            say(
                text="Sorry, I had trouble summarizing the thread. Please try again later.",
                thread_ts=thread_ts,
            )
        finally:
            try:
                client.reactions_remove(
                    channel=channel_id, timestamp=message_ts, name="spin-loading"
                )
            except Exception:
                pass


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
