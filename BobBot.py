# Builtin
import logging
from pathlib import Path
# Pip
import discord
# Custom
import Config

# Discord variables
bot = discord.Bot()

# Path variables
rootDirectory = Path(__file__).parent
logPath = rootDirectory.joinpath("Debug Files").joinpath("bot.log")


# Function which runs once the bot is setup and running
async def startup() -> None:
    await bot.wait_until_ready()
    await bot.get_channel(817807544482922496).send("Running")


# Setup automatic logging for debugging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=logPath, encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

# Load extensions
for extension in [f"Cogs.{file.name.replace('.py', '')}" for file in rootDirectory.joinpath("Cogs").glob("*.py")]:
    bot.load_extension(extension)

# Start discord bot
bot.loop.create_task(startup())
bot.run(Config.token)
