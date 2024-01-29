from __future__ import annotations

import os

from discord import app_commands, Interaction, Embed, Colour
from discord.ext import commands

from .utils.rcon_client import RconClient


class Rcon(commands.Cog, name="Rcon"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.rcon_client: RconClient = RconClient(
            host=os.getenv("RCON_HOST"),
            password=os.getenv("RCON_PASSWORD"),
            port=os.getenv("RCON_PORT"),
        )
        self.steam_profile = "https://steamcommunity.com/profiles/{steam_id}/"

    @app_commands.command(name="rcon_commands", description="Get the list of rcon commands")
    async def rcon_commands(self, interaction: Interaction) -> None:
        embed = Embed(title="Rcon Commands", colour=Colour.blurple())
        embed.add_field(name="Info", value="Get the server info")
        embed.add_field(name="Save", value="Save the server")
        embed.add_field(name="ShowPlayers", value="Get the list of players online")
        embed.add_field(name="Broadcast", value="Broadcast a message to the server")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="online", description="Get the list of players online")
    async def online(self, interaction: Interaction) -> None:
      output, players = self.rcon_client.online()
      if not output:
          await interaction.response.send_message("There was an error getting the list of players online.")
          return
      embed = Embed(title="Players Online", colour=Colour.blurple(), description=f"Player(s) Online: {len(players)}")
      list_of_players = ""
      for player in players:
          list_of_players += f"[{player[0]}]({self.steam_profile.format(steam_id=player[1])})\n"
      embed.add_field(name="Players", value=list_of_players, inline=False)
      await interaction.response.send_message(embed=embed)
         
    @app_commands.command(name="rcon_info", description="Get the server info")
    async def rcon_info(self, interaction: Interaction) -> None:
          info = self.rcon_client.info()
          if not info:
              await interaction.response.send_message("There was an error getting the server info.")
              return
          embed = Embed(title="Server Info", colour=Colour.blurple(), description=info)
          await interaction.response.send_message(embed=embed)

  
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Rcon(client))
