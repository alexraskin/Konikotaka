from discord import Interaction, app_commands
from discord.ext import commands

from models.snad import SnadCounter
from datetime import datetime
from models.db import Base


class SnadFun(commands.Cog, name="Fun"):
  def __init__(self, client: commands.Bot):
    self.client = client
    Base.metadata.create_all(self.client.engine, checkfirst=True)
    self.snad_count = self.client.db_session.query(SnadCounter).count()

  @commands.command(name="snad", description="How many times has Snad been caught?")
  async def snad(self, ctx: commands.Context):
    """Snad counter"""
    message = f"Snad has been caught {self.snad_count} times! "
    await ctx.send(message)

  @commands.command(name="addsnad")
  async def add_snad(self, ctx: commands.Context):
    """Snad has been caught again!"""
    d_date = datetime.datetime.now()
    reg_format_date = d_date.strftime("%Y-%m-%d %I:%M:%S %p")
    print(reg_format_date)
    await ctx.send(reg_format_date)
    try:
      self.snad_count = SnadCounter(
        count=self.snad_count + 1,
        caught=reg_format_date
      )
      self.client.db_session.add(self.snad_count)
      self.client.db_session.commit()
      await ctx.send(f"Snad has been caught {self.snad_count + 1} times!")
    except Exception as e:
      print(e)
      self.client.db_session.rollback()
      await ctx.send("An error occurred while adding Snad.", ephemeral=True)

async def setup(client):
  await client.add_cog(SnadFun(client))
