from typing import Optional

import discord
import wavelink
from discord import app_commands, Interaction
from discord.ext import commands


class Music(commands.Cog, name="Music"):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
        self.client.log.info(f"Node {node.id} is ready!")

    @app_commands.command(name="play", description="Search a song on Youtube\nExample: /play Never Gonna Give You Up")
    @app_commands.guild_only()
    @app_commands.describe(search="The search query to use.")
    @app_commands.describe(volume="The volume to play at.")
    async def play(
        self, interaction: Interaction, search: str, volume: Optional[int] = 30
    ) -> None:
        """
        Play a song from YouTube.
        """

        if search is None:
            await interaction.response.send_message("Please provide a search query.")
            return

        if volume > 100 or volume < 0:
            await interaction.response.send_message("Volume must be between 0 and 100")
            return

        if await self.check_author(interaction) is False:
            return
        
        author_voice = interaction.user.voice

        player: wavelink.Player = interaction.guild.voice_client or await author_voice.channel.connect(cls=wavelink.Player)
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
                await interaction.response.send_message(embed=embed)
            else:
                await player.queue.put_wait(tracks[0])
                await interaction.response.send_message(f"Queued {tracks[0].title}")

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
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"Queued Playlist")

        else:
            await interaction.response.send_message("No results found")

    @app_commands.command(name="stop", description="Stop the current song")
    @app_commands.guild_only()
    async def stop(self, interaction: Interaction) -> None:
        """Stop the current song"""
        if await self.check_author(interaction) is False:
            return
        player: wavelink.Player = interaction.guild.voice_client
        if player.queue.is_empty != True:
            player.queue.clear()
        await player.disconnect()
        await interaction.response.send_message("Stopped! ⏹️")

    @app_commands.command(name="now_playing", description="Show the current song")
    @app_commands.guild_only()
    async def now_playing(self, interaction: Interaction) -> None:
        """Show the current song"""
        if await self.check_author(interaction) is False:
            return
        player: wavelink.Player = interaction.guild.voice_client
        if not player.is_playing():
            await interaction.response.send_message("Nothing is playing")
            return
        embed = discord.Embed(
            title="Now Playing ▶️", description=player.current.title, color=0x00FF00
        )
        embed.set_image(url=player.current.thumbnail)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pause", description="Pause the current song")
    @app_commands.guild_only()
    async def pause(self, interaction: Interaction) -> None:
        """
        Pause the player.
        """
        if await self.check_author(interaction) is False:
            return
        player: wavelink.Player = interaction.guild.voice_client
        await player.pause()
        await interaction.response.send_message(content="Paused! ⏸️")

    @app_commands.command(name="resume", description="Resume the current song")
    @app_commands.guild_only()
    async def resume(self, interaction: Interaction) -> None:
        """
        Resume the player.
        """
        if await self.check_author(interaction) is False:
            return
        player: wavelink.Player = interaction.guild.voice_client
        await player.resume()
        await interaction.response.send_message(content="Resumed! ⏯️")

    @app_commands.command(name="volume", description="Set the player volume")
    @app_commands.guild_only()
    @app_commands.describe(volume="The volume to play at.")
    async def volume(self, interaction: Interaction, volume: int) -> None:
        """
        Set the player volume.
        """
        if await self.check_author(interaction) is False:
            return
        if volume is None:
            await interaction.response.send_message(
                f"Current volume {interaction.guild.voice_client.volume}"
            )
            return
        if volume > 100 or volume < 0:
            await interaction.response.send_message("Volume must be between 0 and 100")
            return
        player: wavelink.Player = interaction.guild.voice_client
        await player.set_volume(volume)
        await interaction.response.send_message(content=f"Set volume to {volume}. 🔊")

    @app_commands.command(name="queue", description="Show the current queue")
    @app_commands.guild_only()
    async def queue(self, interaction: Interaction) -> None:
        """Show the current queue"""
        if await self.check_author(interaction) is False:
            return
        player: wavelink.Player = interaction.guild.voice_client
        if player.queue.is_empty:
            await interaction.response.send_message("Queue is empty")
            return
        embed = discord.Embed(title="Queue ", description="", color=0x00FF00)
        for i, track in enumerate(player.queue, start=1):
            embed.description += f"{i}) {track.title}\n"
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove", description="Remove a song from queue")
    @app_commands.guild_only()
    async def remove(self, interaction: Interaction, index: int) -> None:
        """Remove a song from queue"""
        if await self.check_author(interaction) is False:
            return
        player: wavelink.Player = interaction.guild.voice_client
        if player.queue.is_empty:
            await interaction.response.send_message("Queue is empty")
            return
        if index > len(player.queue):
            await interaction.response.send_message("Index out of range")
            return
        del player.queue[index - 1]
        await interaction.response.send_message("Removed! ✅")

    async def check_author(self, interaction: Interaction) -> bool:
        if interaction.user.voice is None:
            await interaction.response.send_message("Join a voice channel first..")
            return False
        return True


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Music(client))
