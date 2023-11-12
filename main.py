from agent.agent import Agent
from discord_bot import DiscordBot


agent = Agent()
discord_bot = DiscordBot(agent)
discord_bot.run()