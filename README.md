# ThreadSummarizer

ThreadSummarizer is a Slack bot that summarizes your long threads into a statement that you can understand! (powered by AI!)

Features:

- Summarize Slack Threads via:
  - DMs! (Send the bot a thread link and summarize it easily!)
  - @mention the bot in a thread!
  - Use a shortcut on a thread to summarize it!
- Many summary styles!
  - Short
  - Detailed
  - TL:DR
  - Fuwwy (easter egg shhh)

- You can send summaries to your
  - DMs
  - Or the original thread


## Requirements
- Python (duh! specifically 3.13 or above)
- A Slack Bot created
  - You can use SlackManifest.yaml to create it easily and insert the Bot and App tokens in the .env file.
- An AI endpoint and model compatible with OpenAI


## Quick Start

1. Clone this repo

```bash
    git clone https://github.com/Snowflake6413/threadsummarizer
    cd ThreadSummarizer
```
2. Fill in envs in the .env.example file

3. Install dependencies with ``uv sync``

```bash
    uv sync
```
4. Run the bot
```bash
    python bot.py
```

## Usage

You can send the bot a thread link to summarize it, use the message shortcut or @mention it in a thread!

## License

This repo is licensed under the MIT license. Read [LICENSE] for more infomation.
