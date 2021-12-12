# Builtin
from math import ceil
from typing import TYPE_CHECKING, Optional, List, Any
# Pip
import discord
import lavapy
from lavapy.ext import spotify
# Custom
import Config
from Utils.Paginator import Paginator

if TYPE_CHECKING:
    from BobBot import BobBot


# Custom Lavapy Player class to add additional functionality
class CustomPlayer(lavapy.Player):
    def __init__(self, bot, channel: discord.VoiceChannel) -> None:
        super().__init__(bot, channel)
        self.context: Optional[discord.ApplicationContext] = None

    async def playNext(self) -> None:
        # Test if the queue is empty
        if self.queue.isEmpty:
            # All tracks done so disconnect and cleanup
            await self.context.send("Finished playing all tracks. Disconnecting")
            await self.destroy()
        else:
            # Play the next track
            await self.play(self.queue.next())


# Cog to manage music commands
class Music(discord.Cog):
    def __init__(self, bot) -> None:
        self.bot: BobBot = bot
        self.color = discord.Color.blue()

    async def startup(self):
        """Runs once the bot is up and running."""
        # Wait until the bot is ready
        await self.bot.wait_until_ready()
        await lavapy.NodePool.createNode(client=self.bot,
                                         host="192.168.1.227",
                                         port=2333,
                                         password="",
                                         region=discord.VoiceRegion.london,
                                         spotifyClient=spotify.SpotifyClient(clientID=Config.spotifyID,
                                                                             clientSecret=Config.spotifySecret),
                                         identifier="Main Node")

    @staticmethod
    def listSplit(arr: List[Any], perListSize: int) -> List[List[Any]]:
        """
        Splits a list with a set amount of item in each sublist.

        Parameters
        ----------
        arr: List[Any]
            The list to split.

        perListSize: int
            How many items should be in each sublist.

        Returns
        -------
        List[List[Any]]
            The splitted list.
        """
        result = []
        for i in range(ceil(len(arr)/perListSize)):
            result.append(arr[i * perListSize:i * perListSize + perListSize])
        return result

    @staticmethod
    async def joinChannel(ctx: discord.ApplicationContext,
                          channel: discord.VoiceChannel = None
                          ) -> None:
        """Joins a voice channel."""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.respond("You must be in a voice channel in order to use this command.")
                return
        # noinspection PyTypeChecker
        player: CustomPlayer = await channel.connect(cls=CustomPlayer)
        player.context = ctx
        await ctx.respond(f"Joined the voice channel {channel.mention}")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def connect(self,
                      ctx: discord.ApplicationContext,
                      channel: discord.Option(discord.VoiceChannel, "The voice channel to connect to", required=False)
                      ) -> None:
        """Connects the bot to a given voice channel or to the one the user is currently connected to."""
        await self.joinChannel(ctx, channel)

    @discord.slash_command(guild_ids=[682249251543449601])
    async def disconnect(self,
                         ctx: discord.ApplicationContext
                         ) -> None:
        """Disconnects the bot from a voice channel if it is are connected."""
        if not ctx.voice_client:
            await ctx.respond("You must be in a voice channel in order to use this command.")
            return
        # Get the player which is currently playing
        player: CustomPlayer = ctx.voice_client
        await player.destroy()
        await ctx.respond("Player has left the channel.")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def play(self,
                   ctx: discord.ApplicationContext,
                   query: discord.Option(str, "The query to search for. This could be a search query or a URL")
                   ) -> None:
        """Searches for and plays a given search query or URL."""
        if not ctx.voice_client:
            # Bot not in voice channel
            await self.joinChannel(ctx)
        player: CustomPlayer = ctx.voice_client
        if not player:
            # Bot couldn't join channel since the user wasn't connected
            return
        # Find out what track type it is and then search it
        if "spotify.com" in query:
            searchType = spotify.decodeSpotifyQuery(query)
        else:
            searchType = lavapy.decodeQuery(query)
        result = await searchType.search(query, partial=True)
        if result is None:
            await ctx.respond("No results were found for that search")
            return
        # If the player is already playing, push result to the queue
        if player.isPlaying:
            if isinstance(result, lavapy.MultiTrack):
                player.queue.addIterable(result.tracks)
            else:
                player.queue.add(result)
            return
        await player.play(result)

    @discord.slash_command(guild_ids=[682249251543449601])
    async def pause(self,
                    ctx: discord.ApplicationContext
                    ) -> None:
        """Pauses the currently playing track."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        if player.isPaused:
            await ctx.respond("Bot is already paused")
            return
        await player.pause()
        await ctx.respond("Bot has been paused")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def resume(self,
                     ctx: discord.ApplicationContext
                     ) -> None:
        """Resumes the currently playing track."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        if not player.isPaused:
            await ctx.respond("Bot is already playing")
            return
        await player.resume()
        await ctx.respond("Bot has been resumed")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def stop(self,
                   ctx: discord.ApplicationContext
                   ) -> None:
        """Stops the currently playing track."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        if not player.isPlaying:
            await ctx.respond("Bot is already stopped")
            return
        await player.stop()
        await ctx.respond("Bot has been stopped")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def next(self,
                   ctx: discord.ApplicationContext
                   ) -> None:
        """Plays the next song in the queue."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        try:
            track = player.queue.next()
        except lavapy.QueueEmpty:
            await ctx.respond("Queue is empty.")
            return
        except lavapy.RepeatException:
            await ctx.respond("Cannot get next track while the bot is repeating")
            return
        await player.play(track)
        await ctx.respond(f"Now playing {player.track.title}")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def previous(self,
                       ctx: discord.ApplicationContext
                       ) -> None:
        """Plays the previous song in the queue."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        try:
            track = player.queue.previous()
        except lavapy.QueueEmpty:
            await ctx.respond("Queue is empty")
            return
        except lavapy.RepeatException:
            await ctx.respond("Cannot get previous track while the bot is repeating")
            return
        await player.play(track)
        await ctx.respond(f"Now playing {player.track.title}")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def queue(self,
                    ctx: discord.ApplicationContext
                    ) -> None:
        """Displays the current queue."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        try:
            tracks = player.queue.tracks
        except lavapy.QueueEmpty:
            await ctx.respond("Queue is empty.")
            return
        # Split up tracks into sublists of 20 tracks each
        pages = []
        splittedTracks = self.listSplit(tracks, 20)
        for count, sublist in enumerate(splittedTracks):
            tempEmbed = discord.Embed(title=f"Page {count+1} of {len(splittedTracks)}", colour=self.color)
            tempEmbed.set_footer(text=f"Track Total: {len(tracks)}")
            tempDescription = ""
            for position, track in enumerate(sublist):
                # Display currently playing track
                if track == player.track:
                    tempDescription += "► "
                # Display the track position and query ('track - author name' for full tracks)
                if isinstance(track, lavapy.Track):
                    tempDescription += f"{(count*20)+position+1}. {track.title} - {track.author}\n"
                elif isinstance(track, lavapy.PartialResource):
                    tempDescription += f"{(count*20)+position+1}. {track.query} (Partial)\n"
            tempEmbed.description = tempDescription
            pages.append(tempEmbed)
        # Paginate the response
        paginator = Paginator(pages)
        await paginator.respond(ctx.interaction)

    @discord.slash_command(guild_ids=[682249251543449601])
    async def repeat(self,
                     ctx: discord.ApplicationContext
                     ) -> None:
        """Toggles repeating of the current track."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        print(player.isRepeating)
        if player.isRepeating:
            player.stopRepeat()
            await ctx.respond("Stopped repeating the current track")
        else:
            player.repeat()
            await ctx.respond("Repeating the current track")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def shuffle(self,
                      ctx: discord.ApplicationContext
                      ) -> None:
        """Shuffles the queue leaving the current track in the same place."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        player.queue.shuffle()
        await ctx.respond("Shuffled the queue")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def volume(self,
                     ctx: discord.ApplicationContext,
                     volume: discord.Option(int, "The volume to set the bot to", min_value=0, max_value=1000)
                     ) -> None:
        """Shuffles the queue leaving the current track in the same place."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        await player.setVolume(volume)
        await ctx.respond(f"Set bot volume to {volume}")

    @discord.slash_command(guild_ids=[682249251543449601])
    async def current(self,
                      ctx: discord.ApplicationContext
                      ) -> None:
        """Displays the currently playing track."""
        if not ctx.voice_client:
            await ctx.respond("Bot is not connected to voice")
            return
        player: CustomPlayer = ctx.voice_client
        if player.track is None:
            await ctx.respond("Bot is not playing")
            return
        currentEmbed = discord.Embed(title=f"Currently Playing: {player.track.author} - {player.track.title}", colour=self.color)
        currentEmbed.url = player.track.uri
        if isinstance(player.track, lavapy.YoutubeTrack):
            currentEmbed.set_image(url=player.track.thumbnail)
        await ctx.respond(embed=currentEmbed)


def setup(bot) -> None:
    bot.add_cog(Music(bot))
