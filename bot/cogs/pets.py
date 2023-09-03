from models.db import Base, engine, async_session

from discord.ext import commands, tasks
from discord import Embed

from models.db_helper import DBHelper


class Pets(commands.Cog, name='Feed Cats'):
  def __init__(self, client: commands.Bot):
    self.client = client

  @tasks.loop(count=1)
  async def init_database(self):
      async with engine.begin() as conn:
         await conn.run_sync(Base.metadata.create_all)

  @commands.group(name="pets", invoke_without_command=True)
  async def pets(self, ctx: commands.Context):
    """Pets commands"""
    await ctx.send_help(ctx.command)

  @pets.command(name="createpet")
  async def create(self, ctx: commands.Context, pet_name: str):
    """Create a pet"""
    async with async_session() as session:
      async with session.begin():
        db_helper = DBHelper(session)
        pet = await db_helper.get_user_pet(ctx.author.id)
        if pet is not None:
          await ctx.send("You already have a pet.")
          return
        await db_helper.add_new_user_pet(ctx.author.id, pet_name)
        await ctx.send(f"Your pet {pet_name} has been created.")

  @pets.command(name="feed")
  async def feed(self, ctx: commands.Context):
    """Feed your pet"""
    async with async_session() as session:
      async with session.begin():
        db_helper = DBHelper(session)
        pet = await db_helper.get_user_pet(ctx.author.id)
        if pet is None:
          await ctx.send("You don't have a pet. Use `pets create` to create one.")
          return
        if pet.hunger >= 100:
          await ctx.send(f"{pet.pet_name} is full.")
          return
        pet.hunger += 10
        await session.commit()
        await ctx.send(f"You fed {pet.pet_name}.")

  @pets.command(name="play")
  async def play(self, ctx: commands.Context):
    """Play with your pet"""
    async with async_session() as session:
      async with session.begin():
        db_helper = DBHelper(session)
        pet = await db_helper.get_user_pet(ctx.author.id)
        if pet is None:
          await ctx.send("You don't have a pet. Use `pets create` to create one.")
          return
        if pet.happiness >= 100:
          await ctx.send(f"{pet.pet_name} is happy.")
          return
        pet.happiness += 10
        await session.commit()
        await ctx.send(f"You played with {pet.pet_name}.")
  
  @pets.command(name="treat")
  async def treat(self, ctx: commands.Context):
    """Give your pet a treat"""
    async with async_session() as session:
      async with session.begin():
        db_helper = DBHelper(session)
        pet = await db_helper.get_user_pet(ctx.author.id)
        if pet is None:
          await ctx.send("You don't have a pet. Use `pets create` to create one.")
          return
        pet.treat_count += 1
        await session.commit()
        await ctx.send(f"You gave {pet.pet_name} a treat.")

  @pets.command(name="stats")
  async def stats(self, ctx: commands.Context):
    """Display your pet's stats"""
    async with async_session() as session:
      async with session.begin():
        db_helper = DBHelper(session)
        pet = await db_helper.get_user_pet(ctx.author.id)
        if pet is None:
          await ctx.send("You don't have a pet. Use `pets create` to create one.")
          return
        embed = Embed(title=f"{pet.pet_name}'s Stats")
        embed.add_field(name="Hunger", value=f"{pet.hunger}/100")
        embed.add_field(name="Happiness", value=f"{pet.happiness}/100")
        embed.add_field(name="Treats", value=f"{pet.treat_count}")
        await ctx.send(embed=embed)
      
  @pets.command(name="leaderboard")
  async def leaderboard(self, ctx: commands.Context):
    """Display the leaderboard"""
    async with async_session() as session:
      async with session.begin():
        db_helper = DBHelper(session)
        pets = await db_helper.get_all_pets()
        embed = Embed(title="Pet Leaderboard")
        embed.add_field(name="Hunger", value="\n".join([f"{pet.pet_name}: {pet.hunger}/100" for pet in pets]))
        embed.add_field(name="Happiness", value="\n".join([f"{pet.pet_name}: {pet.happiness}/100" for pet in pets]))
        embed.add_field(name="Treats", value="\n".join([f"{pet.pet_name}: {pet.treat_count}" for pet in pets]))
        await ctx.send(embed=embed)

async def setup(client: commands.Bot):
  cog = Pets(client)
  await cog.init_database()
  client.add_cog(cog)
