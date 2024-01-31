from __future__ import annotations

import os

from discord import app_commands, Interaction, Embed, Colour
from discord.ext import commands
from discord.ext.commands import GroupCog
from discord.app_commands import command

from .utils.rcon_client import RconClient


class Rcon(
    GroupCog,
    group_name="palworld",
    group_description="Avaliable commands to interact with the Palworld Server",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.rcon_client: RconClient = RconClient(
            host=os.getenv("RCON_HOST"),
            password=os.getenv("RCON_PASSWORD"),
            port=int(os.getenv("RCON_PORT")),
        )
        self.steam_profile = "https://steamcommunity.com/profiles/{steam_id}/"

    @command(name="commands", description="Get the list of Palworld Server commands")
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_commands(self, interaction: Interaction) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        embed = Embed(title="Rcon Commands", colour=Colour.blurple())
        embed.add_field(name="Info", value="Get the server info")
        embed.add_field(name="Save", value="Save the server")
        embed.add_field(name="ShowPlayers", value="Get the list of players online")
        embed.add_field(name="Broadcast", value="Broadcast a message to the server")
        embed.add_field(name="Kick", value="Kick a player from the server")
        embed.add_field(name="Ban", value="Ban a player from the server")
        embed.add_field(name="Shutdown", value="Shutdown the server")

        embed.set_footer(text="Note: Commands only available to admins")
        await interaction.response.send_message(embed=embed)

    @command(
        name="online",
        description="Get the list of players online in our Palworld Server",
    )
    @app_commands.checks.has_role(1201576683355000852)
    async def online(self, interaction: Interaction) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        output, players = self.rcon_client.online()
        if not output:
            await interaction.response.send_message(
                "There was an error getting the list of players online."
            )
            return
        embed = Embed(
            title="Players Online",
            colour=Colour.blurple(),
            description=f"Player(s) Online: {len(players)}",
        )
        list_of_players = ""
        for player in players:
            list_of_players += (
                f"[{player[0]}]({self.steam_profile.format(steam_id=player[1])})\n"
            )
        embed.add_field(name="Players", value=list_of_players, inline=False)
        await interaction.response.send_message(embed=embed)

    @command(name="info", description="Get the server info")
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_info(self, interaction: Interaction) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        info = self.rcon_client.info()
        if not info:
            await interaction.response.send_message(
                "There was an error getting the server info."
            )
            return
        embed = Embed(title="Server Info", colour=Colour.blurple(), description=info)
        await interaction.response.send_message(embed=embed)

    @command(name="save", description="Save the palworld server")
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_save(self, interaction: Interaction) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        output = self.rcon_client.save()
        if not output:
            await interaction.response.send_message(
                "There was an error saving the server."
            )
            return
        await interaction.response.send_message("Server saved successfully. 🎉")

    @command(name="broadcast", description="Broadcast a message to the server")
    @app_commands.describe(message="The message to broadcast")
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_broadcast(self, interaction: Interaction, message: str) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        output = self.rcon_client.announce(message)
        if not output:
            await interaction.response.send_message(
                "There was an error broadcasting the message."
            )
            return
        await interaction.response.send_message("Message broadcasted successfully. 🎉")

    @command(name="kick", description="Kick a player from the server")
    @app_commands.describe(steam_id="The steam id of the player to kick")
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_kick(self, interaction: Interaction, steam_id: str) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        output = self.rcon_client.kick(steam_id)
        if not output:
            await interaction.response.send_message(
                "There was an error kicking the player."
            )
            return
        await interaction.response.send_message("Player kicked successfully.")

    @command(name="ban", description="Ban a player from the server")
    @app_commands.describe(steam_id="The steam id of the player to ban")
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_ban(self, interaction: Interaction, steam_id: str) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        output = self.rcon_client.ban(steam_id)
        if not output:
            await interaction.response.send_message(
                "There was an error banning the player."
            )
            return
        await interaction.response.send_message("Player banned successfully.")

    @command(name="shutdown", description="Shutdown the server")
    @app_commands.describe(
        seconds="The number of seconds to wait before shutting down the server"
    )
    @app_commands.describe(
        message="The message to broadcast before shutting down the server"
    )
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_shutdown(
        self, interaction: Interaction, seconds: str, message: str
    ) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )
        output = self.rcon_client.shutdown(seconds, message)
        if not output:
            await interaction.response.send_message(
                "There was an error shutting down the server."
            )
            return
        await interaction.response.send_message(
            "Server shutting down in {seconds} seconds. Please prepare to disconnect from the server. 🎉"
        )

    @command(name="force_stop", description="Force stop the server")
    @app_commands.checks.has_role(1201576683355000852)
    async def rcon_force_stop(self, interaction: Interaction) -> None:
        if interaction.guild_id != self.client.main_guild:
            return await interaction.response.send_message(
                "This command is not available in this server."
            )

        output = self.rcon_client.force_stop()
        if not output:
            await interaction.response.send_message(
                "There was an error force stopping the server."
            )
            return
        await interaction.response.send_message("Server force stopped successfully.")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Rcon(client))
