from __future__ import annotations

import datetime
from typing import Optional

from discord import Embed, Interaction, Member, TextChannel, app_commands
from discord.ext import commands


class Mod(commands.Cog, name="Mod"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @app_commands.command(name="amimod", description="Check if you are a mod")
    @app_commands.guild_only()
    async def _amimod(self, interaction: Interaction) -> None:
        if (
            interaction.user.guild_permissions.administrator
            or interaction.user.guild_permissions.manage_guild
        ):
            await interaction.response.send_message(
                "Yes", ephemeral=True, delete_after=5
            )
        else:
            await interaction.response.send_message(
                "No", ephemeral=True, delete_after=5
            )

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.guild_only()
    @app_commands.describe(member="The member to ban")
    @app_commands.describe(reason="The reason for the ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def _ban(self, interaction: Interaction, member: Member, reason: str) -> None:
        await interaction.guild.ban(member, reason=reason)
        await interaction.response.send_message(f"Banned {member.name}", ephemeral=True)

    @app_commands.command(name="softban", description="Softban a user")
    @app_commands.guild_only()
    @app_commands.describe(member="The member to softban")
    @app_commands.describe(reason="The reason for the softban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def _softban(
        self, interaction: Interaction, member: Member, reason: str
    ) -> None:
        await interaction.guild.ban(member, reason=reason)
        await interaction.guild.unban(member, reason=reason)
        await interaction.response.send_message(
            f"Softbanned {member.name}", ephemeral=True
        )

    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.guild_only()
    @app_commands.describe(member="The member to kick")
    @app_commands.describe(reason="The reason for the kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def _kick(
        self, interaction: Interaction, member: Member, reason: str
    ) -> None:
        await interaction.guild.kick(member, reason=reason)
        await interaction.response.send_message(f"Kicked {member.name}", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a user")
    @app_commands.guild_only()
    @app_commands.describe(member="The member to timeout")
    @app_commands.describe(reason="The reason for the timeout")
    @app_commands.describe(duration="The duration of the timeout")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def _timeout(
        self, interaction: Interaction, member: Member, reason: str, duration: int
    ) -> None:
        unmute_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
        await member.timeout(until=unmute_time, reason=reason)
        await interaction.response.send_message(
            f"Timed out {member.name}", ephemeral=True
        )

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.guild_only()
    @app_commands.describe(member="The member to unban")
    @app_commands.describe(reason="The reason for the unban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def _unban(
        self, interaction: Interaction, member: Member, reason: str
    ) -> None:
        await interaction.guild.unban(member, reason=reason)
        await interaction.response.send_message(
            f"Unbanned {member.name}", ephemeral=True
        )

    @app_commands.command(name="purge")
    @app_commands.guild_only()
    @app_commands.describe(amount="The amount of messages to purge.")
    @app_commands.describe(reason="The reason for purging the messages.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(
        self, interaction: Interaction, amount: int, reason: Optional[str] = None
    ) -> None:
        """
        Purges a specified amount of messages from the channel.
        """
        if amount <= 0:
            await interaction.response.send_message(
                "Please specify a positive number of messages to delete."
            )
            return
        try:
            amount += 1
            await interaction.response.defer()
            await interaction.channel.purge(limit=amount, reason=reason)
            embed = Embed(
                title="Purge 🗑️",
                description=f"Purged {amount} messages.",
                color=0x00FF00,
                timestamp=interaction.message.created_at,
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            self.client.log.error(f"Error: {e}")
            await interaction.response.send_message(
                "An error occurred while purging messages.", ephemeral=True
            )
            return

    @commands.hybrid_command(
        name="lockdown", description="Lockdowns a specified channel."
    )
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(
        channel="The channel to lockdown. Defaults to the current channel."
    )
    @app_commands.describe(reason="The reason for locking down the channel.")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lockdown(
        self,
        ctx: commands.Context,
        channel: Optional[TextChannel] = None,
        *,
        reason: Optional[str] = None,
    ) -> None:
        """
        Lockdowns a specified channel.
        """
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            embed = Embed(
                title="Lockdown Notice 🔒",
                description="This channel is currently under lockdown.",
                color=0x00FF00,
                timestamp=ctx.message.created_at,
            )
            if reason:
                embed.add_field(name="Reason:", value=reason)
            embed.set_footer(text="Please be patient and follow server rules")
            await ctx.send(embed=embed)
        except Exception as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send(
                "An error occurred while locking down the channel.", ephemeral=True
            )
            return

    @commands.hybrid_command(name="unlock", description="Unlocks a specified channel.")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(
        channel="The channel to unlock. Defaults to the current channel."
    )
    @app_commands.describe(reason="The reason for unlocking the channel.")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(
        self,
        ctx: commands.Context,
        channel: Optional[TextChannel] = None,
        *,
        reason: Optional[str] = None,
    ) -> None:
        """
        Unlocks a specified channel.
        """
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(
                ctx.guild.default_role, send_messages=True, reason=reason
            )
            embed = Embed(
                title="Lockdown Ended 🔓",
                description="The lockdown has been lifted.",
                color=0x00FF00,
                timestamp=ctx.message.created_at,
            )
            if reason:
                embed.add_field(name="Reason:", value=reason)
            embed.set_footer(text="Please be patient and follow server rules")
            await ctx.send(embed=embed)
        except Exception as e:
            self.client.log.error(f"Error: {e}")
            await ctx.send(
                "An error occurred while unlocking the channel.", ephemeral=True
            )
            return


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Mod(client))
