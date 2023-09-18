from datetime import datetime

from discord import Embed, app_commands
from discord.ext import commands, tasks
from models.db import Base
from models.tags import CustomTags
from sqlalchemy.future import select


class Tags(commands.Cog, name="Custom Tags"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.init_database.start()

    @tasks.loop(count=1)
    async def init_database(self) -> None:
        async with self.client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @commands.hybrid_group(fallback="get")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(tag_name="The tag to get")
    async def tag(self, ctx: commands.Context, tag_name: str) -> None:
        """
        Get a tag
        """
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name)
            )
            tag = query.scalar_one_or_none()
            if tag:
                tag.called = int(str(tag.called).strip()) + 1
                await ctx.send(str(tag.content))
                try:
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()
                    await ctx.reply(
                        "An error occurred while fetching the tag. 👎", ephemeral=True
                    )
            else:
                await ctx.reply(f"Tag `{tag_name}` not found. 👎", ephemeral=True)

    @tag.command()
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(tag_name="The tag to add")
    @app_commands.describe(tag_content="The content of the tag")
    async def add(
        self, ctx: commands.Context, tag_name: str, *, tag_content: str
    ) -> None:
        """
        Add a new tag
        """
        if len(tag_name) > 255:
            return await ctx.reply("Tag name is too long. 👎", ephemeral=True)
        if len(tag_content) > 1000:
            return await ctx.reply("Tag content is too long. 👎", ephemeral=True)
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name)
            )
            tag = query.scalar_one_or_none()
            if tag:
                return await ctx.reply(f"Tag `{tag_name}` already exists 👎", ephemeral=True)
            new_tag = CustomTags(
                name=tag_name.strip(),
                content=tag_content,
                discord_id=ctx.author.id,
                date_added=ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
            )
            try:
                session.add(new_tag)
                await session.flush()
                await session.commit()
                await ctx.reply(f"Tag `{tag_name}` added! 👍")
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()
                await ctx.reply(
                    "An error occurred while adding the tag.", ephemeral=True
                )

    @tag.command()
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(tag_name="The tag to edit")
    @app_commands.describe(tag_content="The new content of the tag")
    async def edit(
        self, ctx: commands.Context, tag_name: str, *, tag_content: str
    ) -> None:
        """
        Edit a tag
        """
        if len(tag_name) > 255:
            return await ctx.reply("Tag name is too long.", ephemeral=True)
        if len(tag_content) > 1000:
            return await ctx.reply("Tag content is too long.", ephemeral=True)
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name)
            )
            tag = query.scalar_one_or_none()
            if tag:
                if int(str(tag.discord_id).strip()) != ctx.author.id:
                    return await ctx.reply("You are not the owner of this tag.", ephemeral=True)
                tag.content = tag_content
                try:
                    await session.flush()
                    await session.commit()
                    await ctx.reply(f"Tag `{tag_name}` edited!")
                except Exception as e:
                    await ctx.reply(
                        "An error occurred while editing the tag.", ephemeral=True
                    )
                    self.client.log.error(e)
                    await session.rollback()
            else:
                await ctx.reply(f"Tag `{tag_name}` not found.", ephemeral=True)

    @tag.command(description="Get info on a tag")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(tag_name="The tag to get info on")
    async def stats(self, ctx: commands.Context, tag_name: str) -> None:
        """
        Get info on a tag
        """
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name)
            )
            tag = query.scalar_one_or_none()
            if tag:
                time = datetime.strptime(tag.date_added, "%Y-%m-%d %H:%M:%S %Z%z")
                embed = Embed(title=f"Tag: {tag.name}", description=tag.content)
                embed.add_field(name="Owner", value=f"<@{tag.discord_id}>")
                embed.add_field(name="Date Added", value=time.strftime("%B %d, %Y"))
                embed.add_field(name="Times Called", value=tag.called)
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(f"Tag `{tag_name}` not found.", ephemeral=True)

    @tag.command()
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(tag_name="The tag to remove")
    async def delete(self, ctx: commands.Context, tag_name: str) -> None:
        """
        Delete a tag
        """
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name)
            )
            tag = query.scalar_one_or_none()
            if int(str(tag.discord_id).strip()) != ctx.author.id:
                return await ctx.reply("You are not the owner of this tag.", ephemeral=True)
            if tag:
                try:
                    session.delete(tag)
                    await session.flush()
                    await session.commit()
                    await ctx.reply(f"Tag `{tag_name}` deleted!")
                    self.client.log.info(
                        f"User {ctx.author} deleted a tag named {tag_name}"
                    )
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()
                    await ctx.reply(
                        "An error occurred while deleting the tag. 👎", ephemeral=True
                    )
            else:
                await ctx.reply(f"Tag `{tag_name}` not found.", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Tags(client))
