import os

from discord.ext import commands, tasks
from models.db import Base
from models.word_count import WordCount


class WordCounter(commands.Cog, name="Word Count"):
    def __init__(self, client) -> None:
        self.client = client
        self.get_words.start()
        self.init_database.start()
        self.bot_channel = os.getenv("BOT_CHANNEL_ID")

    @tasks.loop(count=1)
    async def init_database(self):
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @tasks.loop(minutes=1)
    async def get_words(self):
        async with self.client.async_session() as session:
            self.word_list = (
                (await session.execute(session.query(WordCount).all())).scalars().all()
            )
            self.word_list = [word for word in self.word_list]

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = await self.client.fetch_channel(self.bot_channel)
        if message.author.bot:
            return
        for word in self.word_list:
            if word.word in message.content.lower():
                word.count += 1
                if message.guild.id == self.client.cosmo_guild:
                    if message.channel.id != 1149054364795805779:
                        await channel.send(
                            f"Word `{str(word.word).capitalize()}` has been said {word.count} times."
                        )
                        self.client.db_session.commit()

    @commands.hybrid_command(
        name="addword",
        description="Add a new word to track the amount of times it has been said.",
        with_app_command=True,
    )
    async def add_word(self, ctx: commands.Context, word: str):
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
            session.add(new_word)

            try:
                session.commit()
            except Exception as e:
                self.client.log.error(e)
                session.rollback()

        await ctx.send(f"Word `{word}` added!")
        await ctx.message.add_reaction("👍")
        self.client.log.info(f"Word {word} added by {ctx.author}")

    @commands.hybrid_command(
        name="removeword",
        description="Add a new word to track the amount of times it has been said.",
        with_app_command=True,
    )
    async def remove_word(self, ctx: commands.Context, word: str):
        """
        Add a new word to track the amount of times it has been said.
        """
        if len(word) > 255:
            return await ctx.send("Word is too long.")
        try:
            word = (
                self.client.db_session.query(WordCount)
                .filter(WordCount.word == word)
                .first()
            )
            if word:
                self.client.db_session.delete(word)
                self.client.db_session.commit()
                await ctx.send(f"Word `{word}` removed!")
                await ctx.message.add_reaction("👍")
            else:
                await ctx.send(f"Word `{word}` not found.")
                self.log.client.info(f"Word {word} not found by {ctx.author}")
        except Exception as e:
            self.client.log.error(e)
            self.client.db_session.rollback()
            await ctx.send("An error occurred while removing the word.", ephemeral=True)


async def setup(client):
    await client.add_cog(WordCounter(client))
