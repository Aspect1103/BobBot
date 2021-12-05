# Pip
import discord


# Cog to manage music commands
class Music(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot

    @discord.slash_command(guild_ids=[682249251543449601])
    async def connect(self, ctx: discord.ApplicationContext) -> None:
        pass

    @discord.slash_command(guild_ids=[682249251543449601])
    async def disconnect(self, ctx: discord.ApplicationContext) -> None:
        pass

    @discord.slash_command(guild_ids=[682249251543449601])
    async def play(self, ctx: discord.ApplicationContext) -> None:
        pass

    @discord.slash_command(guild_ids=[682249251543449601])
    async def queue(self, ctx: discord.ApplicationContext) -> None:
        pass

    @discord.slash_command(guild_ids=[682249251543449601])
    async def previous(self, ctx: discord.ApplicationContext) -> None:
        pass

    @discord.slash_command(guild_ids=[682249251543449601])
    async def next(self, ctx: discord.ApplicationContext) -> None:
        pass


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Music(bot))
