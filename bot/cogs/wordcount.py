import os
from typing import List

from discord import Message, app_commands
from discord.ext import commands, tasks
from models.db import Base
from models.word_count import WordCount
from sqlalchemy.future import select


class WordCounter(commands.Cog, name="Word Count"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.get_words.start()
        self.init_database.start()
        self.bot_channel = os.getenv("BOT_CHANNEL_ID")
        self.word_list: List[str] = []

    @tasks.loop(count=1)
    async def init_database(self) -> None:
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @tasks.loop(minutes=1)
    async def get_words(self) -> None:
        async with self.client.async_session() as session:
            query = await session.execute(select(WordCount))
            self.word_list = query.scalars().all()

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        channel = await self.client.fetch_channel(self.bot_channel)
        if message.author.bot:
            return
        for word in self.word_list:
            if word.word in message.content.lower():
                if message.channel.id in self.client.channel_ignore:
                    return
                if message.guild.id == self.client.cosmo_guild:
                    word.count += 1
                    async with self.client.async_session() as session:
                        try:
                            await session.flush()
                            await session.commit()
                        except Exception as e:
                            self.client.log.error(e)
                            await session.rollback()
                    await channel.send(
                        f"Word `{str(word.word).capitalize()}` has been said {word.count} times."
                    )

    @commands.hybrid_command(
        name="addword",
        description="Add a new word to track the amount of times it has been said.",
        with_app_command=True,
    )
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(word="The word to add.")
    async def add_word(self, ctx: commands.Context, word: str) -> None:
        """
        Add a new word to track the amount of times it has been said.
        """
        if len(word) > 255:
            return await ctx.send("Word is too long.")
        new_word = WordCount(
            word=word.strip(),
            discord_id=ctx.author.id,
        )
        async with self.client.async_session() as session:
            try:
                session.add(new_word)
                await session.flush()
                await session.commit()
                await ctx.send(f"Word `{word}` added!")
                await ctx.message.add_reaction("👍")
                self.client.log.info(f"Word {word} added by {ctx.author}")
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()

    @commands.hybrid_command(
        name="removeword",
        description="Add a new word to track the amount of times it has been said.",
        with_app_command=True,
    )
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(word="The word to remove.")
    async def remove_word(self, ctx: commands.Context, word: str) -> None:
        """
        Add a new word to track the amount of times it has been said.
        """
        if len(word) > 255:
            return await ctx.send("Word is too long.")
        async with self.client.async_session() as session:
            query = await session.execute(
                select(WordCount).filter(WordCount.word == word)
            )
            word_ = query.scalar_one_or_none()
            if word_:
                try:
                    session.delete(word_)
                    await session.flush()
                    await session.commit()
                    await ctx.send(f"Word `{word}` removed!")
                    await ctx.message.add_reaction("👍")
                    self.client.log.info(f"Word {word} removed by {ctx.author}")
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()
            else:
                await ctx.send(f"Word `{word}` not found.")
                self.log.client.info(f"Word {word} not found by {ctx.author}")


async def setup(client):
    await client.add_cog(WordCounter(client))
