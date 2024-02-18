from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import discord
import wavelink  # type: ignore
from discord import Colour, app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Konikotaka
    from utils.context import Context


class Music(commands.Cog):
    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
        self.client.log.info(f"Node {node.id} is ready!")

    @commands.hybrid_group(
        name="music", description="Music commands", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def music(self, ctx: Context) -> None:
        """Music commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @music.command(
        name="play", description="Search a song on Youtube, or queue a song!"
    )
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(search="The search query to use.")
    @app_commands.describe(volume="The volume to play at.")
    async def play(self, ctx: Context, search: str, volume: Optional[int] = 30) -> None:
        """
        Play a song from YouTube.
        """

        if search is None:
            await ctx.reply("Please provide a search query.", ephemeral=True)
            return

        if volume > 100 or volume < 0:  # type: ignore
            await ctx.reply("Volume must be between 0 and 100", ephemeral=True)
            return

        if await self.check_author(ctx) is False:
            return

        author_voice = ctx.author.voice

        player: wavelink.Player = (
            ctx.guild.voice_client  # type: ignore
            or await author_voice.channel.connect(cls=wavelink.Player)  # type: ignore
        )
        player.autoplay = True

        tracks = await wavelink.YouTubeTrack.search(search)
        if isinstance(tracks, (list)):
            if not player.is_playing():
                await player.play(tracks[0], populate=True, volume=volume)
                embed = discord.Embed(
                    title="Now Playing",
                    description=f"[{tracks[0].title}]({tracks[0].uri})",
                    color=discord.Color.blurple(),
                )
                embed.set_image(url=tracks[0].thumb)
                await ctx.send(embed=embed)
            else:
                await player.queue.put_wait(tracks[0])
                await ctx.send(f"Queued {tracks[0].title}")

        elif isinstance(tracks, wavelink.YouTubePlaylist):
            await player.queue.put_wait(tracks)
            if not player.is_playing():
                track = player.queue.get()
                await player.play(track, populate=True, volume=volume)
                embed = discord.Embed(
                    title="Now Playing",
                    description=f"[{track.title}]({track.uri})",
                    color=discord.Color.blurple(),
                )
                embed.set_image(url=track.thumb)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Queued Playlist {tracks.title}")

        else:
            await ctx.send("No results found", ephemeral=True)

    @music.command(name="stop", description="Stop the current song")
    @commands.guild_only()
    @app_commands.guild_only()
    async def stop(self, ctx: Context) -> None:
        """Stop the current song"""
        if await self.check_author(ctx) is False:
            return
        player: wavelink.Player = ctx.guild.voice_client  # type: ignore
        if player.queue.is_empty is not True:
            player.queue.clear()
        await player.disconnect()
        await ctx.reply("Stopped! ⏹️")

    @music.command(name="playing", description="Show the current song")
    @commands.guild_only()
    @app_commands.guild_only()
    async def playing(self, ctx: Context) -> None:
        """Show the current song"""
        if await self.check_author(ctx) is False:
            return
        player: wavelink.Player = ctx.guild.voice_client  # type: ignore
        if not player.is_playing():
            await ctx.reply("Nothing is playing")
            return
        embed = discord.Embed(title="Now Playing ▶️", description=player.current.title)
        embed.colour = Colour.blurple()
        embed.set_image(url=player.current.thumbnail)
        await ctx.send(embed=embed)

    @music.command(description="Pause the current song")
    @commands.guild_only()
    @app_commands.guild_only()
    async def pause(self, ctx: Context) -> None:
        """
        Pause the player.
        """
        if await self.check_author(ctx) is False:
            return
        player: wavelink.Player = ctx.guild.voice_client  # type: ignore
        await player.pause()
        await ctx.send(content="Paused! ⏸️")

    @music.command(name="resume", description="Resume the current song")
    @commands.guild_only()
    @app_commands.guild_only()
    async def resume(self, ctx: Context) -> None:
        """
        Resume the player.
        """
        if await self.check_author(ctx) is False:
            return
        player: wavelink.Player = ctx.guild.voice_client  # type: ignore
        await player.resume()
        await ctx.send(content="Resumed! ⏯️")

    @music.command(description="Set the player volume")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(volume="The volume to play at.")
    async def volume(self, ctx: Context, volume: Optional[int]) -> None:
        """
        Set the player volume.
        """
        if await self.check_author(ctx) is False:
            return
        if volume > 100 or volume < 0:  # type: ignore
            await ctx.send("Volume must be between 0 and 100", ephemeral=True)
            return
        player: wavelink.Player = ctx.voice_client
        if volume is None:
            await ctx.send(f"Current volume {player.volume}")
            return
        await player.set_volume(volume)
        await ctx.send(content=f"Set volume to {volume}. 🔊")

    @music.command(name="queue", description="Show the current queue")
    @app_commands.guild_only()
    async def queue(self, ctx: Context) -> None:
        """Show the current queue"""
        if await self.check_author(ctx) is False:
            return
        player: wavelink.Player = ctx.guild.voice_client  # type: ignore
        if player.queue.is_empty:
            await ctx.send("Queue is empty")
            return
        embed = discord.Embed(title="Queue ", description="", color=0x00FF00)
        for i, track in enumerate(player.queue, start=1):
            embed.description += f"{i}) {track.title}\n"  # type: ignore
        await ctx.send(embed=embed)

    @music.command(name="remove", description="Remove a song from queue")
    @app_commands.guild_only()
    async def remove(self, ctx: Context, index: int) -> None:
        """Remove a song from queue"""
        if await self.check_author(ctx) is False:
            return
        player: wavelink.Player = ctx.guild.voice_client  # type: ignore
        if player.queue.is_empty:
            await ctx.send("Queue is empty")
            return
        if index > len(player.queue):
            await ctx.send("Index out of range", ephemeral=True)
            return
        del player.queue[index - 1]
        await ctx.send("Removed! ✅")

    async def check_author(self, ctx: Context) -> bool:
        if ctx.author.voice is None:  # type: ignore
            await ctx.reply("Join a voice channel first..", ephemeral=True)
            return False
        return True


async def setup(client: Konikotaka) -> None:
    await client.add_cog(Music(client))
