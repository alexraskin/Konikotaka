from discord.ext import commands, tasks

from models.word_count import WordCount
from models.db import Base

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class WordCounter(commands.Cog, name="Word Count"):
    def __init__(self, client) -> None:
        self.client = client
        Base.metadata.create_all(self.client.engine, checkfirst=True)
        self.build_word_list.start()

    @tasks.loop(seconds=10)
    async def build_word_list(self):
        self.word_list = (
            self.client.db_session.query(WordCount)
            .order_by(WordCount.count.desc())
            .all()
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        for word in self.word_list:
            if word.word in message.content.lower():
                word.count += 1
                await message.channel.send(
                    f"Word `{word.word}` has been said {word.count} times!"
                )
                self.client.db_session.commit()

    @commands.hybrid_command(
        name="addword", description="Add a new word to track the count of", with_app_command=True
    )
    async def add_word(self, ctx: commands.Context, word: str):
        if len(word) > 255:
            return await ctx.send("Word is too long.")
        try:
            new_word = WordCount(
                word=word.strip(),
                discord_id=ctx.author.id,
            )
            self.client.db_session.add(new_word)
            self.client.db_session.commit()
            await ctx.send(f"Word `{word}` added!")
            await ctx.message.add_reaction("👍")
        except Exception as e:
            log.error(e)
            self.client.db_session.rollback()
            await ctx.send("An error occurred while adding the word.", ephemeral=True)

    @commands.hybrid_command(name="removeword", description="Remove a word from being tracked", with_app_command=True)
    async def remove_word(self, ctx: commands.Context, word: str):
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
        except Exception as e:
            log.error(e)
            self.client.db_session.rollback()
            await ctx.send("An error occurred while removing the word.", ephemeral=True)


async def setup(client):
    await client.add_cog(WordCounter(client))
