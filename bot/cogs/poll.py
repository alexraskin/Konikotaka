from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Konikotaka
    from utils.context import Context


class Polls(commands.Cog):
    """Poll voting system.

    this cog is based on Rapptz's quickpoll cog.
    https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/poll.py
    """

    def __init__(self, client: Konikotaka) -> None:
        self.client: Konikotaka = client

    def to_emoji(self, c: int) -> str:
        base = 0x1F1E6
        return chr(base + c)

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx: Context, *questions_and_choices: str) -> None:
        """Makes a poll quickly.

        The first argument is the question and the rest are the choices.
        """

        if len(questions_and_choices) < 3:
            return await ctx.send("Need at least 1 question with 2 choices.")  # type: ignore
        elif len(questions_and_choices) > 21:
            return await ctx.send("You can only have up to 20 choices.")  # type: ignore

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send(
                "Need Read Message History and Add Reactions permissions."
            )  # type: ignore

        question = questions_and_choices[0]
        choices = [
            (self.to_emoji(e), v) for e, v in enumerate(questions_and_choices[1:])
        ]

        try:
            await ctx.message.delete()
        except Exception:
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        poll = await ctx.send(f"{ctx.author} asks: {question}\n\n{body}")
        for emoji, _ in choices:
            await poll.add_reaction(emoji)


async def setup(client: Konikotaka):
    await client.add_cog(Polls(client))
