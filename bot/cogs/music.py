from typing import Any

import discord
import wavelink
from discord import app_commands
from discord.ext import commands


class Player(wavelink.Player):
    """A Player with a DJ attribute."""

    def __init__(self, dj: discord.Member, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.dj = dj


class Music(commands.Cog, name="Music"):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        super().__init__()

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
        self.client.log.info(f"Node {node.id} is ready!")

    @commands.hybrid_group()
    async def music(self, ctx: commands.Context) -> None:
        """Music commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @music.command()
    @commands.guild_only()
    @app_commands.guild_only()
    async def connect(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel | None = None
    ):
        """
        Connect to a voice channel.
        """
        try:
            channel = channel or ctx.author.channel.voice
        except AttributeError:
            return await ctx.send(
                "No voice channel to connect to. Please either provide one or join one."
            )

        player = Player(dj=ctx.author)
        await channel.connect(cls=player)
        return await ctx.send(content=f"Connected to {channel.name}.")

    @music.command()
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(search="The search query to use.")
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        """
        Play a song from YouTube.
        """
        if not ctx.voice_client:
            vc: Player = await ctx.author.voice.channel.connect(cls=Player)
        else:
            vc: Player = ctx.voice_client

        tracks = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.send(content=f"No tracks found with query: `{search}`")
            return

        track = tracks[0]
        await vc.play(track)
        await ctx.send(content=f"Playing track: `{track.title}`")

    @music.command()
    @commands.guild_only()
    @app_commands.guild_only()
    async def stop(self, ctx: commands.Context) -> None:
        """
        Stop the player.
        """
        vc: Player = ctx.voice_client
        await vc.disconnect()
        await ctx.send(content="Disconnected!")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Music(client))
