from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from discord import Embed
from discord.ext import commands
from discord.ext.commands import DefaultHelpCommand, HelpCommand

if TYPE_CHECKING:
    from ..bot import Konikotaka


class myHelpCommand(HelpCommand):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.paginator = None
        self.spacer: str = " "

    async def send_pages(self, header=False, footer=False) -> None:
        destination = self.get_destination()
        embed = Embed(color=0x2ECC71, timestamp=self.context.message.created_at)
        if header:
            embed.set_author(name=self.context.bot.description)
        for category, entries in self.paginator:  # type: ignore
            embed.add_field(name=category, value=entries, inline=False)
        if footer:
            embed.set_footer(text="Use !help <command/category> for more information.")
        await destination.send(embed=embed)

    async def send_bot_help(self, mapping: dict):
        ctx = self.context
        bot = ctx.bot

        def get_category(command: commands.Command):
            cog = command.cog
            return cog.qualified_name + ":" if cog is not None else "Help:"

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)
        for cog_name, command_grouper in to_iterate:
            cmds = sorted(command_grouper, key=lambda c: c.name)
            category = f"► {cog_name}"
            if len(cmds) == 1:
                entries = f"{self.spacer}{cmds[0].name} → {cmds[0].short_doc}"
            else:
                entries = ""
                while len(cmds) > 0:
                    entries += self.spacer
                    entries += " | ".join([cmd.name for cmd in cmds[0:8]])
                    cmds = cmds[8:]
                    entries += "\n" if cmds else ""
            self.paginator.append((category, entries))  # type: ignore
        await self.send_pages(header=True, footer=True)

    async def send_cog_help(self, cog: commands.Cog):
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        if not filtered:
            await self.context.send(
                "No public commands in this cog. Try again with !helpall."
            )
            return
        category = f"▼ {cog.qualified_name}"
        entries = "\n".join(
            self.spacer
            + f"**{command.name}** → {command.short_doc or command.description}"
            for command in filtered
        )
        self.paginator.append((category, entries))  # type: ignore
        await self.send_pages(footer=True)

    async def send_group_help(self, group: commands.group):  # type: ignore
        filtered = await self.filter_commands(group.commands, sort=True)
        if not filtered:
            await self.context.send(
                "No public commands in group. Try again with !helpall"
            )
            return
        category = f"**{group.name}** - {group.description or group.short_doc}"
        entries = "\n".join(
            self.spacer + f"**{command.name}** → {command.short_doc}"
            for command in filtered
        )
        self.paginator.append((category, entries))  # type: ignore
        await self.send_pages(footer=True)

    async def send_command_help(self, command: commands.Command):
        signature = self.get_command_signature(command)
        helptext = command.help or command.description or "No help Text"
        self.paginator.append((signature, helptext))  # type: ignore
        await self.send_pages()

    async def prepare_help_command(self, ctx: commands.Context, command=None):
        self.paginator = []
        await super().prepare_help_command(ctx, command)


class Help(commands.Cog):
    def __init__(self, client: Konikotaka):
        self.client: Konikotaka = client
        self.client.help_command = myHelpCommand(
            command_attrs={
                "aliases": ["halp"],
                "help": "Shows help about the bot, a command, or a category",
            }
        )

    def cog_unload(self):
        self.client.get_command("help").hidden = False  # type: ignore
        self.client.help_command = DefaultHelpCommand()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def helpall(self, ctx, *, text=None):
        self.client.help_command = myHelpCommand(show_hidden=True)
        if text:
            await ctx.send_help(text)
        else:
            await ctx.send_help()
        self.client.help_command = myHelpCommand()


async def setup(client: Konikotaka):
    await client.add_cog(Help(client))
