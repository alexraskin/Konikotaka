from discord.ext import commands

from models.snad import SnadCounter
from datetime import datetime
from models.db import Base


class SnadFun(commands.Cog, name="Fun"):
    def __init__(self, client: commands.Bot):
        self.client = client
        Base.metadata.create_all(self.client.engine, checkfirst=True)

    @commands.command(name="snad", description="How many times has Snad been caught?")
    async def snad(self, ctx: commands.Context):
        """Snad counter"""
        snad_count = self.client.db_session.query(SnadCounter).count()
        await ctx.send(
            f"Snad has been caught {snad_count} times! <:LULW:1146225785515016342>"
        )

    @commands.command(name="addsnad")
    async def add_snad(self, ctx: commands.Context):
        try:
            count = self.client.db_session.query(SnadCounter).all()
            snad_count = SnadCounter(count=len(count), caught=datetime.now())
            self.client.db_session.add(snad_count)
            self.client.db_session.commit()
            await ctx.send(
                f"Snad has been caught {len(count) + 1} times! <:LULW:1146225785515016342>"
            )
        except Exception as e:
            print(e)
            self.client.db_session.rollback()
            await ctx.send("An error occurred while adding Snad.", ephemeral=True)


async def setup(client):
    await client.add_cog(SnadFun(client))
