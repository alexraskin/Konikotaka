import discord
from discord.ext import commands
from PIL import Image
from io import BytesIO
import os


class Fight(commands.Cog, name="Fight"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    
    @commands.hybrid_command(name="fight", description="Fight with someone!")
    async def fight(self, ctx: commands.Context, user: discord.User):
      try:
        ava1 = await self.client.session.get(ctx.author.avatar.url)
        ava2 = await self.client.session.get(user.avatar.url)
        avatar1_data = await ava1.read()
        avatar2_data = await ava2.read()
        avatar1 = Image.open(BytesIO(avatar1_data))
        avatar2 = Image.open(BytesIO(avatar2_data))


        canvas_width, canvas_height = 400, 200
        fight_scene = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))

        # Calculate the position to center the avatars on the canvas
        avatar_width, avatar_height = avatar1.size
        x_offset = (canvas_width - avatar_width * 2) // 2
        y_offset = (canvas_height - avatar_height) // 2

        # Paste avatars onto the fight scene
        fight_scene.paste(avatar1, (x_offset, y_offset))
        fight_scene.paste(avatar2, (x_offset + avatar_width, y_offset))

        # Save the fight scene as a temporary image
        fight_scene.save("fight_scene.png")

        # Send the fight scene image to the Discord channel
        await ctx.send("The fight begins!")
        with open("fight_scene.png", "rb") as f:
            await ctx.send(file=discord.File(f))
            await ctx.send(f"{ctx.author.mention} and {user.mention} are fighting!")
            await ctx.send("I am still working on this command, so it is not finished yet!")
            os.remove("fight_scene.png")
      except Exception as e:
         print(e)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Fight(client))
