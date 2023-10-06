from __future__ import annotations

import asyncio
import random
from datetime import datetime
from typing import Optional, Union

import discord
from discord import Embed, PartialEmoji, TextStyle, app_commands
from discord.ext import commands
from discord.interactions import Interaction
from models.tags import CustomTags
from sqlalchemy.future import select


class TagName(commands.clean_content):
    def __init__(self, *, lower: bool = False):
        self.lower: bool = lower
        super().__init__()

    async def convert(self, ctx: commands.Context, argument: str) -> str:
        converted = await super().convert(ctx, argument)
        lower = converted.lower().strip()

        if not lower:
            raise commands.BadArgument("Missing tag name.")

        if len(lower) > 255:
            raise commands.BadArgument("Tag name is a maximum of 100 characters.")

        first_word, _, _ = lower.partition(" ")

        root: commands.GroupMixin = ctx.bot.get_command("tag")  # type: ignore
        if first_word in root.all_commands:
            raise commands.BadArgument("This tag name starts with a reserved word.")

        return converted.strip() if not self.lower else lower


class CreateTagModel(discord.ui.Modal, title="Create New Tag"):
    tag_name = discord.ui.TextInput(
        label="Tag Name",
        style=TextStyle.short,
        placeholder="Tag Name",
        required=True,
        max_length=255,
    )
    tag_content = discord.ui.TextInput(
        label="Tag Content",
        style=TextStyle.paragraph,
        placeholder="Tag Content",
        required=True,
        max_length=2000,
    )

    def __init__(self, ctx: commands.Context, cog: Tags) -> None:
        super().__init__(timeout=60.0)
        self.cog: commands.Cog = cog
        self.ctx: commands.Context = ctx

    async def on_submit(self, interaction: Interaction) -> None:
        name = str(self.tag_name.value)
        await interaction.response.defer()
        try:
            name = await TagName().convert(self.ctx, name)
        except commands.BadArgument as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        content = str(self.tag_content.value)
        if len(content) > 2000:
            await interaction.response.send_message(
                "Tag content is a maximum of 2000 characters.", ephemeral=True
            )
        await self.cog.add_tag(self.ctx, name, content)


class EditTagModel(discord.ui.Modal, title="Edit Tag"):
    tag_name = discord.ui.TextInput(
        label="Tag Name",
        style=TextStyle.short,
        placeholder="Tag Name",
        required=True,
        max_length=255,
    )
    new_tag_content = discord.ui.TextInput(
        label="New Tag Content",
        style=TextStyle.paragraph,
        placeholder="Tag Content",
        required=True,
        max_length=2000,
    )

    def __init__(self, ctx: commands.Context, cog: Tags) -> None:
        super().__init__(timeout=60.0)
        self.cog: commands.Cog = cog
        self.ctx: commands.Context = ctx

    async def on_submit(self, interaction: Interaction) -> None:
        name = str(self.tag_name.value)
        content = str(self.new_tag_content.value)
        await interaction.response.defer()
        try:
            name = await TagName().convert(self.ctx, name)
        except commands.BadArgument as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        if len(content) > 2000:
            await interaction.response.send_message(
                "Tag content is a maximum of 2000 characters.", ephemeral=True
            )
        await self.cog.edit_tag(self.ctx, name, content)


class Tags(commands.Cog, name="Custom Tags"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @property
    def display_emoji(self) -> PartialEmoji:
        return PartialEmoji(name="cosmo")

    async def add_tag(
        self, ctx: commands.Context, tag_name: str, tag_content: str
    ) -> None:
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name.lower())
            )
            tag = query.scalar_one_or_none()
            if tag:
                return await ctx.reply(
                    f"Tag `{tag_name}` already exists 👎", ephemeral=True
                )
            new_tag = CustomTags(
                name=tag_name.strip().lower(),
                content=tag_content,
                discord_id=str(ctx.author.id),
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

    async def edit_tag(
        self, ctx: commands.Context, tag_name: str, tag_content: str
    ) -> None:
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name)
            )
            tag = query.scalar_one_or_none()
            if tag is None:
                return await ctx.reply(
                    f"Tag `{tag_name}` does not exist 👎", ephemeral=True
                )
            if tag:
                if int(str(tag.discord_id).strip()) != ctx.author.id:
                    return await ctx.reply(
                        "You are not the owner of this tag.", ephemeral=True
                    )
                new_tag = CustomTags(
                    name=tag_name.strip().lower(),
                    content=tag_content,
                    discord_id=str(ctx.author.id),
                    date_added=ctx.message.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S %Z%z"
                    ),
                )
                try:
                    session.add(new_tag)
                    await session.flush()
                    await session.commit()
                    await ctx.reply(f"Tag `{tag_name}` has been updated! 👍")
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()
                    await ctx.reply(
                        "An error occurred while updating the tag.", ephemeral=True
                    )

    async def lookup_similar_tags(self, tag_name: str) -> Optional[list[CustomTags]]:
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).where(CustomTags.name.like(f"%{tag_name.lower()}%"))
            )
            tags = query.scalars().all()
            if tags:
                return tags
            else:
                return None

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
                select(CustomTags).filter(CustomTags.name == tag_name.lower())
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
                tags = await self.lookup_similar_tags(tag_name)
                if tags:
                    await ctx.reply(
                        content=f"Tag `{tag_name}` not found. Did you mean one of these?\n"
                        + "\n".join([f"{tag.name}" for tag in tags])
                    )
                else:
                    await ctx.reply(f"Tag `{tag_name}` not found", ephemeral=True)

    @tag.command()
    @commands.guild_only()
    @app_commands.guild_only()
    async def add(self, ctx: commands.Context) -> None:
        """
        Add a new tag
        """
        if ctx.interaction is not None:
            modal = CreateTagModel(ctx, self)
            await ctx.interaction.response.send_modal(modal)
            return

        def check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        await ctx.send("Hello. What would you like the tag's name to be?")

        converter = TagName()
        original = ctx.message

        try:
            name = await self.client.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took long. Goodbye.")

        try:
            ctx.message = name
            name = await converter.convert(ctx, name.content)
        except commands.BadArgument as e:
            return await ctx.send(
                f'{e}. Redo the command "{ctx.prefix}tag make" to retry.'
            )
        finally:
            ctx.message = original

        await ctx.send(
            f"Neat. So the name is `{name}`. What about the tag's content? "
            f"**You can type {ctx.prefix}abort to abort the tag make process.**"
        )

        try:
            msg = await self.client.wait_for("message", check=check, timeout=300.0)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Goodbye.")

        if msg.content == f"{ctx.prefix}abort":
            return await ctx.send("Aborting...")

        elif msg.content:
            try:
                clean_content = await commands.clean_content().convert(ctx, msg.content)
            except Exception as e:
                return await ctx.send(
                    f'{e}. Redo the command "{ctx.prefix}tag make" to retry.'
                )
        else:
            clean_content = msg.content

        if msg.attachments:
            clean_content = f"{clean_content}\n{msg.attachments[0].url}"

        if len(clean_content) > 2000:
            return await ctx.send("Tag content is a maximum of 2000 characters.")

        await self.add_tag(ctx, name, clean_content)

    @tag.command()
    @commands.guild_only()
    @app_commands.guild_only()
    async def edit(self, ctx: commands.Context):
        """
        Edit a tag
        """
        if ctx.interaction is not None:
            modal = EditTagModel(ctx, self)
            await ctx.interaction.response.send_modal(modal)
            return

        def check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        await ctx.send("Hello. Which tag would you like to edit?")

        converter = TagName()
        original = ctx.message

        try:
            name = await self.client.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took long. Goodbye.")

        try:
            ctx.message = name
            name = await converter.convert(ctx, name.content)
        except commands.BadArgument as e:
            return await ctx.send(
                f'{e}. Redo the command "{ctx.prefix}tag edit" to retry.'
            )
        finally:
            ctx.message = original

        await ctx.send(
            f"Neat. So the tag you would like to edit is `{name}`. What about the tag's content? "
            f"**You can type {ctx.prefix}abort to abort the tag edit process.**"
        )

        try:
            msg = await self.client.wait_for("message", check=check, timeout=300.0)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Goodbye.")

        if msg.content == f"{ctx.prefix}abort":
            return await ctx.send("Aborting...")

        elif msg.content:
            try:
                clean_content = await commands.clean_content().convert(ctx, msg.content)
            except Exception as e:
                return await ctx.send(
                    f'{e}. Redo the command "{ctx.prefix}tag edit" to retry.'
                )
        else:
            clean_content = msg.content

        if msg.attachments:
            clean_content = f"{clean_content}\n{msg.attachments[0].url}"

        if len(clean_content) > 2000:
            return await ctx.send("Tag content is a maximum of 2000 characters.")

        await self.edit_tag(ctx, name, clean_content)

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
                select(CustomTags).filter(CustomTags.name == tag_name.lower())
            )
            tag = query.scalar_one_or_none()
            if tag:
                time = datetime.strptime(tag.date_added, "%Y-%m-%d %H:%M:%S %Z%z")
                embed = Embed(title=f"Tag: {tag.name}", description=tag.content)
                embed.colour = Colour.blurple()
                embed.add_field(name="Owner", value=f"<@{tag.discord_id}>")
                embed.add_field(name="Date Added", value=time.strftime("%B %d, %Y"))
                embed.add_field(name="Times Called", value=tag.called)
                embed.set_footer(text=f"ID: {tag.id}")
                await ctx.reply(embed=embed)
            else:
                tags = await self.lookup_similar_tags(tag_name)
                if tags:
                    await ctx.reply(
                        content=f"Tag `{tag_name}` not found. Did you mean one of these?\n"
                        + "\n".join([f"`{tag.name}`" for tag in tags])
                    )
                else:
                    await ctx.reply(f"Tag `{tag_name}` not found", ephemeral=True)

    @tag.command(description="List all tags")
    @commands.guild_only()
    @app_commands.guild_only()
    async def all(self, ctx: commands.Context) -> None:
        """
        List all tags
        """
        async with self.client.async_session() as session:
            query = await session.execute(select(CustomTags))
            tags = query.scalars().all()
            if tags:
                if len(tags) > 2000:
                    return await ctx.reply(
                        "There are too many tags to list.", ephemeral=True
                    )
                await ctx.reply(
                    content=f"Here are all the tags:\n"
                    + "\n".join([f"`{tag.name}`" for tag in tags])
                )
            else:
                await ctx.reply("There are no tags.", ephemeral=True)

    @tag.command(description="Search for a tag")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(tag_name="The tag to search for")
    async def search(self, ctx: commands.Context, tag_name: str) -> None:
        """
        Search for a tag
        """
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).where(CustomTags.name.like(f"%{tag_name.lower()}%"))
            )
            tags = query.scalars().all()
            if tags:
                if len(tags) > 2000:
                    return await ctx.reply(
                        "There are too many tags to list.", ephemeral=True
                    )
                await ctx.reply(
                    content=f"Here are all the tags:\n"
                    + "\n".join([f"`{tag.name}`" for tag in tags])
                )
            else:
                await ctx.reply("There are no tags.", ephemeral=True)

    @tag.command(description="Get a random tag")
    @commands.guild_only()
    @app_commands.guild_only()
    async def random(self, ctx: commands.Context) -> None:
        """
        Get a random tag
        """
        async with self.client.async_session() as session:
            query = await session.execute(select(CustomTags))
            tags = query.scalars().all()
            if tags:
                tag = tags[random.randint(0, len(tags) - 1)]
                await ctx.reply(f"TagName:{tag.name}\nTagContent{tag.content}")
            else:
                await ctx.reply("There are no tags.", ephemeral=True)

    @tag.command(description="Transfer a tag to another user")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(tag_name="The tag to transfer")
    @app_commands.describe(member="The member to transfer the tag to")
    async def transfer(
        self,
        ctx: commands.Context,
        tag_name: str,
        member: Union[discord.Member, discord.User],
    ) -> None:
        """
        Transfer a tag to another user
        """
        async with self.client.async_session() as session:
            query = await session.execute(
                select(CustomTags).filter(CustomTags.name == tag_name.lower())
            )
            tag = query.scalar_one_or_none()
            if tag:
                try:
                    tag.discord_id = member.id
                    await session.flush()
                    await session.commit()
                    await ctx.reply(f"Tag `{tag_name}` transferred!")
                    self.client.log.info(
                        f"User {ctx.author} transferred a tag named {tag_name}"
                    )
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()
                    await ctx.reply(
                        "An error occurred while transferring the tag. 👎",
                        ephemeral=True,
                    )
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
                select(CustomTags).filter(CustomTags.name == tag_name.lower())
            )
            tag = query.scalar_one_or_none()
            if tag:
                if int(str(tag.discord_id).strip()) != ctx.author.id:
                    return await ctx.reply(
                        "You are not the owner of this tag.", ephemeral=True
                    )
                try:
                    await session.delete(tag)
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
