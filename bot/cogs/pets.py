import os

from discord import Embed
from discord.ext import commands
from models.db import Base
from models.pet import Pet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



class Pets(commands.Cog, name="Pets"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.engine = create_engine(os.getenv("MYSQL_URL"))
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine)
        self.pets = self.session.query(Pet).all()


    @commands.command(name="create")
    async def create(self, ctx: commands.Context, pet_name: str):
        """Create a pet"""
        try:
            # Check if the user already has a pet
            existing_pet = self.session.query(Pet).filter(Pet.discord_id == ctx.author.id).first()
            
            if existing_pet:
                await ctx.send("You already have a pet.")
            else:
                
                pet = Pet(discord_id=ctx.author.id, pet_name=pet_name)
                self.session.add(pet)
                self.session.commit()
                await ctx.send(f"Created pet {pet_name}.")
        except Exception as e:
            # Handle exceptions, e.g., database errors
            self.session.rollback()  # Rollback the transaction in case of an error
            await ctx.send("An error occurred while creating your pet.")
            print(f"Error: {e}")
      
    @commands.command(name="feed")
    async def feed(self, ctx: commands.Context, pet_name: str, quantity: int = 1):
        """Feed your pet"""
        try:
            # Check if the user already has a pet
            pet = self.session.query(Pet).filter(Pet.pet_name == pet_name).first()
            
            if pet:
                pet.hunger += quantity
                self.session.commit()
                await ctx.send(f"Your pet {pet_name} has been fed {quantity} treats.")
            else:
                await ctx.send(f"You don't have a pet named {pet_name}.")
        except Exception as e:
            await ctx.send("An error occurred while feeding your pet.")
            self.session.rollback()


async def setup(client: commands.Bot):
    cog = Pets(client)
    await client.add_cog(cog)
