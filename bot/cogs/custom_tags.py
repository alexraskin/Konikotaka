import logging
from datetime import datetime

from discord import Embed, app_commands
from discord.ext import commands, tasks
from models.db import Base
from models.tags import CustomTags
from sqlalchemy.future import select

logging.basicConfig(level=logging.INFO)


class Tags(commands.Cog, name="Custom Tags"):
    def __init__(self, client) -> None:
        self.client = client
        self.init_database.start()

    @tasks.loop(count=1)
    async def init_database(self):
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @commands.hybrid_group(fallback="get")
    @commands.guild_only()
    @app_commands.describe(tag_name="The tag to get")
    async def tag(self, ctx: commands.Context, tag_name: str):
        """
        Get a tag
        """
        async with self.client.async_session() as session:
            query = await session.execute(select(CustomTags).filter(CustomTags.name == tag_name))
            tag = query.scalar_one_or_none()
            if tag is None:
                query = await session.query(select(CustomTags)).filter(CustomTags.name.like(f"%{tag_name}%"))
                similar_tags = [row[0] for row in query.scalars()]
                if len(similar_tags) > 0:
                    await ctx.send("Did you mean one of these tags?\n" + "\n".join([f"`{tag.name}`" for tag in similar_tags]))
                    return

            if tag:
                tag.called = int(str(tag.called).strip()) + 1
                try:
                  await session.commit()
                  await session.flush()
                except Exception as e:
                  self.client.log.error(e)
                  await session.rollback()
                  await ctx.send("An error occurred while fetching the tag.", ephemeral=True)
                await ctx.send(tag.content)
            else:
                await ctx.send(f"Tag `{tag_name}` not found.")

    @commands.hybrid_group(fallback="add")
    @commands.guild_only()
    @app_commands.describe(tag_name="The tag to add")
    @app_commands.describe(tag_content="The content of the tag")
    async def tagadd(self, ctx: commands.Context, tag_name: str, *, tag_content: str):
        """
        Add a new tag
        """
        if len(tag_name) > 255:
            return await ctx.send("Tag name is too long.")
        if len(tag_content) > 1000:
            return await ctx.send("Tag content is too long.")
        tag = CustomTags(
            name=tag_name.strip(),
            content=tag_content,
            discord_id=ctx.author.id,
            date_added=ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        )
        async with self.client.async_session() as session:
            try:
                await session.add(tag)
                await session.commit()
                await self.db_session.flush()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()
        message = await ctx.send(f"Tag `{tag_name}` added!")
        await message.add_reaction("👍")
        self.client.log.info(f"User {ctx.author} added a tag named {tag_name}")

    @tag.command(aliases=["edit"])
    @commands.guild_only()
    @app_commands.describe(tag_name="The tag to edit")
    @app_commands.describe(tag_content="The new content of the tag")
    async def tagedit(self, ctx: commands.Context, tag_name: str, *, tag_content: str):
        """
        Edit a tag
        """
        if len(tag_name) > 255:
            return await ctx.send("Tag name is too long.")
        if len(tag_content) > 1000:
            return await ctx.send("Tag content is too long.")
        async with self.client.async_session() as session:
            query = await session.execute(select(CustomTags).filter(CustomTags.name == tag_name))
            tag = query.scalar_one_or_none()
            if tag:
                if int(str(tag.discord_id).strip()) != ctx.author.id:
                    return await ctx.send("You are not the owner of this tag.")
                tag.content = tag_content
                try:
                    await session.commit()
                    await session.flush()
                except Exception as e:
                    await ctx.send(
                        "An error occurred while editing the tag.", ephemeral=True
                    )
                    self.client.log.error(e)
                    await session.rollback()
                await ctx.send(f"Tag `{tag_name}` edited!")
            else:
                await ctx.send(f"Tag `{tag_name}` not found.")

    @tag.command(aliases=["info"])
    @commands.guild_only()
    @app_commands.describe(tag_name="The tag to get info on")
    async def stats(self, ctx: commands.Context, tag_name: str):
       async with self.client.async_session() as session:
          query = await session.execute(select(CustomTags).filter(CustomTags.name == tag_name))
          tag = query.scalar_one_or_none()     
          if tag:
              time = datetime.strptime(tag.date_added, "%Y-%m-%d %H:%M:%S %Z%z")
              embed = Embed(title=f"Tag: {tag.name}", description=tag.content)
              embed.add_field(name="Owner", value=f"<@{tag.discord_id}>")
              embed.add_field(name="Date Added", value=time.strftime("%B %d, %Y"))
              embed.add_field(name="Times Called", value=tag.called)
              await ctx.send(embed=embed)
          else:
              await ctx.send(f"Tag `{tag_name}` not found.")

    @stats.error
    async def stats_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument: `tag_name`")
        else:
            self.client.log.error(error)
            await ctx.send("An error occurred while fetching the tag.", ephemeral=True)

    @tag.command(aliases=["delete"])
    @commands.guild_only()
    @app_commands.describe(tag_name="The tag to remove")
    async def tagdel(self, ctx: commands.Context, tag_name: str):
        """
        Delete a tag
        """
        async with self.client.async_session() as session:
            query = await session.execute(select(CustomTags).filter(CustomTags.name == tag_name))
            tag = query.scalar_one_or_none()
            if int(str(tag.discord_id).strip()) != ctx.author.id:
                return await ctx.send("You are not the owner of this tag.")
            if tag:
                await session.delete(tag)
                try:
                  await session.commit()
                  await session.flush()
                except Exception as e:
                  self.client.log.error(e)
                  await session.rollback()
                  await ctx.send("An error occurred while deleting the tag.", ephemeral=True)
                await ctx.send(f"Tag `{tag_name}` deleted!")
            else:
                await ctx.send(f"Tag `{tag_name}` not found.")

async def setup(client):
    await client.add_cog(Tags(client))
