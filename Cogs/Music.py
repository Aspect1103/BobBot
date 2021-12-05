# Pip
import discord


# Cog to manage music commands
class Music(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot

    @discord.slash_command(guild_ids=[682249251543449601])
    async def hello(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("Hello")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Music(bot))
