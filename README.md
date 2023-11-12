# assistant

## setup

You must have access to the OpenAI API and an iCloud email account to use this.

1. Create an empty file `.env` in this directory.
2. Create a new Discord server.
3. Create a Discord bot and save its token as `DISCORD_BOT_TOKEN` in `.env`.
4. Add this Discord bot to your new server.
5. Save your OpenAI API key as `OPENAI_API_KEY` in `.env`.
6. Create an iCloud app-specific password and save it as `ICLOUD_PASSWORD` in `.env`.
7. Create an Assistant within the OpenAI API and save its ID as `ASSISTANT_ID` in `.env`.
8. Add each function from `functions.jsonl` to your Assistant.
9. Run `main.py` and interact with the assistant on your new server.