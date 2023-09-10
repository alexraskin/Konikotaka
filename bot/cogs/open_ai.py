import os


import openai
from discord import app_commands
from discord.ext import commands


class OpenAI(commands.Cog, name="Open AI"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.openai = openai
        self.openai.api_key = os.getenv("OPENAI_API_KEY")
      
  
    @commands.hybrid_command(name="imagine")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @app_commands.describe(prompt="The prompt to generate an image from")
    async def imagine(self, ctx, *, prompt):
        """
        Generate an image using OpenAI's image API
        """
        if ctx.guild.id != self.client.cosmo_guild:
            return await ctx.send("This command is not available in this server.")
        message = await ctx.send("Generating image...")
        image_resp = openai.Image.create(prompt=prompt, n=1, size="512x512")
        await message.edit(content=image_resp['data'][0]['url'])
    
    @commands.hybrid_command(name="write")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @app_commands.describe(prompt="The prompt to generate text from")
    async def write(self, ctx, *, prompt):
        """
        Generate text using OpenAI's text API
        """
        if ctx.guild.id != self.client.cosmo_guild:
            return await ctx.send("This command is not available in this server.")
        message = await ctx.send("Generating text...")
        text_resp = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=100)
        await message.edit(content=text_resp['choices'][0]['text'])


async def setup(client):
    await client.add_cog(OpenAI(client))
