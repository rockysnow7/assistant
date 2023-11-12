from agent.agent import Agent
from dotenv import load_dotenv
from typing import Any, Coroutine

import discord
import os


load_dotenv()


class DiscordBot:
    def __init__(self, agent: Agent) -> None:
        self.__agent = agent

        intents = discord.Intents.default()
        intents.message_content = True
        self.__client = discord.Client(intents=intents)

        @self.__client.event
        async def on_ready() -> None:
            print(f"{self.__client.user.name} is connected!")

        @self.__client.event
        async def on_message(message: discord.Message) -> Coroutine[Any, Any, discord.Message | None]:
            if message.author == self.__client.user:
                return

            response = self.__agent.get_response(message.content)

            await message.channel.send(response)

    def run(self) -> None:
        self.__client.run(os.getenv("DISCORD_BOT_TOKEN"))