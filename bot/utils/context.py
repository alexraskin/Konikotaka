from __future__ import annotations

import io
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    TypeVar,
    Union,
    Optional,
)

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Konikotaka
    from aiohttp import ClientSession


T = TypeVar("T")


class Context(commands.Context):
    channel: Union[
        discord.VoiceChannel, discord.TextChannel, discord.Thread, discord.DMChannel
    ]
    prefix: str
    command: commands.Command[Any, ..., Any]
    client: Konikotaka

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def entry_to_code(self, entries: Iterable[tuple[str, str]]) -> None:
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"{name:<{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    async def indented_entry_to_code(self, entries: Iterable[tuple[str, str]]) -> None:
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"\u200b{name:>{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    @property
    def session(self) -> ClientSession:
        return self.client.session

    @discord.utils.cached_property
    def replied_reference(self) -> Optional[discord.MessageReference]:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

    @discord.utils.cached_property
    def replied_message(self) -> Optional[discord.Message]:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved
        return None

    async def show_help(self, command: Any = None) -> None:
        """Shows the help command for the specified command if given.

        If no command is given, then it'll show help for the current
        command.
        """
        cmd = self.client.get_command("help")
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)  # type: ignore

    async def safe_send(
        self, content: str, *, escape_mentions: Optional[bool] = True, **kwargs
    ) -> discord.Message:
        """Same as send except with some safe guards.

        1) If the message is too long then it sends a file with the results instead.
        2) If ``escape_mentions`` is ``True`` then it escapes mentions.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            fp = io.BytesIO(content.encode())
            kwargs.pop("file", None)
            return await self.send(
                file=discord.File(fp, filename="message_too_long.txt"), **kwargs
            )
        else:
            return await self.send(content)
