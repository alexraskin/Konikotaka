from discord.ext import commands

from models.tags import CustomTags
from models.db import Base


class Tags(commands.Cog, name="Custom Tags"):
    def __init__(self, client) -> None:
        self.client = client
        Base.metadata.create_all(self.client.engine, checkfirst=True)

    @commands.command(name="tag", description="Lookup a tag")
    async def tag(self, ctx: commands.Context, tag_name: str):
        try:
            tag = (
                self.client.db_session.query(CustomTags)
                .filter(CustomTags.name == tag_name)
                .first()
            )
            if tag:
                await ctx.send(tag.content)
            else:
                await ctx.send(f"Tag `{tag_name}` not found.")
        except Exception as e:
            print(e)
            await ctx.send("An error occurred while fetching the tag.", ephemeral=True)

    @commands.command(name="addtag", description="Add a new tag")
    async def add_tag(self, ctx: commands.Context, tag_name: str, *, tag_content: str):
        if len(tag_name) > 255:
            return await ctx.send("Tag name is too long.")
        if len(tag_content) > 1000:
            return await ctx.send("Tag content is too long.")
        try:
            tag = CustomTags(
                name=tag_name.strip(), content=tag_content, discord_id=ctx.author.id
            )
            self.client.db_session.add(tag)
            self.client.db_session.commit()
            await ctx.send(f"Tag `{tag_name}` added!")
        except Exception as e:
            print(e)
            self.client.db_session.rollback()
            await ctx.send("An error occurred while adding the tag.", ephemeral=True)

    @commands.command(name="deltag", description="Delete a tag")
    async def del_tag(self, ctx: commands.Context, tag_name: str):
        try:
            tag = (
                self.client.db_session.query(CustomTags)
                .filter(CustomTags.name == tag_name)
                .first()
            )
            if tag:
                self.client.db_session.delete(tag)
                self.client.db_session.commit()
                await ctx.send(f"Tag `{tag_name}` deleted!")
            else:
                await ctx.send(f"Tag `{tag_name}` not found.")
        except Exception as e:
            print(e)
            self.client.db_session.rollback()
            await ctx.send("An error occurred while deleting the tag.", ephemeral=True)


async def setup(client):
    await client.add_cog(Tags(client))
