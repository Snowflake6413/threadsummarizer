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

# This is real.
BLACKLIST_MODE = os.getenv("FUNNY2_BOOLEAN")
BLACKLIST_IDS = os.getenv("FUNNY2_IDS")


# Sys Prompt
sys_prompt = """You are a concise, professional assistant that summarizes Slack threads.

When summarizing, focus on:
- The main topic or problem being discussed
- Key decisions made or conclusions reached
- Action items or next steps (if any)
- Who is responsible for what (if mentioned)

Adjust your output based on the requested style:
- Short: 2-3 sentences max, just the core outcome
- Detailed: Full breakdown with context, decisions, and action items
- TL;DR: One sentence, the absolute bottom line
- Fuwwy: Summarize in a fun, uwu/furry internet style while still conveying the key points

Be neutral and factual. Do not editorialize or add information not present in the thread."""

# OpenAI
smart_client = OpenAI(api_key=AI_KEY, base_url=AI_API_URL)
# Sentry
sentry_sdk.init(dsn=SENTRY_DSN, enable_logs=True)

app = App(token=SLACK_BOT_TOKEN)


@app.command("/ping-20")
def pong(ack, respond):
    ack()
    respond("Pong!", response_type="ephemeral")


@app.view("summarize_modal_callback")
def handle_summarize(ack, body, client, logger, view):
    ack()

    values = view["state"]["values"]
    style = values["style_block"]["style_action"]["selected_option"]["value"]
    delivery = values["delivery_block"]["delivery_action"]["selected_option"]["value"]

    private_metadata = view["private_metadata"]
    if not private_metadata:
        return

    channel_id, thread_ts = private_metadata.split("|")
    user_id = body["user"]["id"]

    try:
        result = client.conversations_replies(channel=channel_id, ts=thread_ts)
        messages = result.get("messages", [])

        thread_content = []
        for msg in messages:
            text = msg.get("text", "")
            thread_content.append(f"User: {text}")
        read_text = "\n".join(thread_content)

        ai_rspnd = smart_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": sys_prompt,
                },
                {
                    "role": "user",
                    "content": f"Style requested: {style}\n\nSummarize this Slack thread: \n\n{read_text}",
                },
            ],
        )

        summary = ai_rspnd.choices[0].message.content

        sum_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Thread Summary (ss style)",
                    "emoji": True,
                },
            },
            {
                "type": "context",
                "elements": [
                    {"type": "plain_text", "text": "Model Used:", "emoji": True}
                ],
            },
        ]

        summary_text = (
            f"*Thread Summary* ({style} style):\n{summary}\n_Requested by <@{user_id}>_"
        )
        if delivery == "dms":
            client.chat_postMessage(channel=user_id, text=summary_text)
        else:
            client.chat_postMessage(
                channel=channel_id, thread_ts=thread_ts, text=summary_text
            )

    except Exception as e:
        print(f"Error handling modal submission! {e}")


@app.shortcut("action_sum")
def summary_menu(ack, shortcut, client):
    ack()

    trigger_id = shortcut["trigger_id"]

    channel_id = shortcut.get("channel", {}).get("id")
    message_ts = shortcut.get("message_ts")
    private_metadata = f"{channel_id}|{message_ts}"

    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "summarize_modal_callback",
            "private_metadata": private_metadata,
            "title": {
                "type": "plain_text",
                "text": "Summarization Options",
                "emoji": True,
            },
            "submit": {"type": "plain_text", "text": "Summarize", "emoji": True},
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Options for your summarization!",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "block_id": "style_block",
                    "text": {
                        "type": "mrkdwn",
                        "text": "What style do you want for your summarization?",
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True,
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Short",
                                    "emoji": True,
                                },
                                "value": "short",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Detailed",
                                    "emoji": True,
                                },
                                "value": "detailed",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Fuwwy",
                                    "emoji": True,
                                },
                                "value": "fuwwy",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "TL:DR",
                                    "emoji": True,
                                },
                                "value": "tldr",
                            },
                        ],
                        "action_id": "style_action",
                    },
                },
                {
                    "type": "input",
                    "block_id": "delivery_block",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True,
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "DMs",
                                    "emoji": True,
                                },
                                "value": "dms",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "In Thread",
                                    "emoji": True,
                                },
                                "value": "thread",
                            },
                        ],
                        "action_id": "delivery_action",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Do you want to forward the summarization to your DMs or in the thread? ",
                        "emoji": True,
                    },
                    "optional": False,
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "plain_text",
                            "text": "Be aware, if you select to forward it to the thread, a message will be sent in the thread notifying that you requested a summarization.",
                            "emoji": True,
                        }
                    ],
                },
            ],
        },
    )


@app.event("app_mention")
def summarize_magic_mention(event, client, say, ack, respond):
    ack()

    if LOCKDOWN_MODE and event.get("channel") != LOCKDOWN_ID:
        thread_ts = event.get("thread_ts")
        say(text="cannot do the funny :( :xdd:", thread_ts=thread_ts)
        return

    if BLACKLIST_MODE and event.get("channel") == BLACKLIST_IDS:
        thread_ts = event.get("thread_ts")
        say(
            text="Unable to summarize! This channel is on the blacklist.",
            thread_ts=thread_ts,
        )
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
                    respond(
                        say="This thread was already summarized.", thread_ts=thread_ts
                    )
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
                        "content": sys_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this Slack thread: \n\n{read_text}",
                    },
                ],
            )

            summary = ai_rspnd.choices[0].message.content

            sum_blocks = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Thread Summary:*\n{summary}"},
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"Model Used: '{AI_MODEL}"}
                    ],
                },
            ]

            say(blocks=sum_blocks, thread_ts=thread_ts)

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
