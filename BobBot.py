# Builtin
import logging
from pathlib import Path
# Pip
import discord
# Custom
import Config

# Path variables
rootDirectory = Path(__file__).parent
logPath = rootDirectory.joinpath("Debug Files").joinpath("bot.log")


# Subclass to add global bot functionality
class BobBot(discord.Bot):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self.errorColor = discord.Color.from_rgb(0, 0, 0)


# Function which runs once the bot is set up and running
async def startup() -> None:
    await bot.wait_until_ready()
    # Run startup functions for each cog
    for cog in bot.cogs.values():
        await cog.startup()
    await bot.get_channel(817807544482922496).send("Running")


# Discord variables
bot = BobBot()

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
