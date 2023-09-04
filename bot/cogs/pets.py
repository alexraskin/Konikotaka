import os
import random

from discord import Embed, Interaction, app_commands
from discord.ext import commands, tasks
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
        self.remove_hunger.start()

    @tasks.loop(minutes=30)
    async def remove_hunger(self):
        for pet in self.pets:
            pet.hunger -= 1
        self.session.commit()

    @tasks.loop(minutes=1)
    async def update_happiness(self):
        for pet in self.pets:
            if pet.hunger > 5:
                pet.happiness += 1
            else:
                pet.happiness -= 1
        self.session.commit()

    @app_commands.command(name="newpet")
    async def create(self, interaction: Interaction, pet_name: str):
        """Create a new pet"""
        try:
            existing_pet = (
                self.session.query(Pet)
                .filter(Pet.discord_id == interaction.user.id)
                .first()
            )
            if existing_pet:
                await interaction.response.send_message(
                    f"You already have a pet! Use `/givetreat <pet_name>` to feed it. <:susspongebob:1145087128087302164>"
                )
            else:
                pet = Pet(discord_id=interaction.user.id, pet_name=pet_name)
                self.session.add(pet)
                self.session.commit()
                await interaction.response.send_message(
                    f"Your pet **{str(pet_name).capitalize()}** has been created! <:wiseoldman:1147920787471347732>"
                )
        except Exception as e:
            self.session.rollback()
            await interaction.response.send_message(
                "An error occurred while creating your pet.", ephemeral=True
            )
            print(f"Error: {e}")

    @app_commands.command(name="givetreat")
    async def feed(self, interaction: Interaction):
        """Feed your pet"""
        try:
            owned_pet = (
                self.session.query(Pet)
                .filter(Pet.discord_id == interaction.user.id)
                .first()
            )
            if not owned_pet:
                await interaction.response.send_message(
                    "You don't have a pet! Use `/newpet <pet_name>` to create one."
                )
                return
            quantity = random.randint(1, 10)
            if quantity > owned_pet.treat_count:
                await interaction.response.send_message(
                    f"You don't have enough treats to feed **{str(owned_pet.pet_name).capitalize()}**! <:susspongebob:1145087128087302164>"
                )
                return
            owned_pet.hunger += quantity
            self.session.commit()
            await interaction.response.send_message(
                f"Your pet **{str(owned_pet.pet_name).capitalize()}** has been fed **{quantity}** treat{'s' if quantity > 1 else ''}! <:wiseoldman:1147920787471347732>"
            )
        except Exception as e:
          await interaction.response.send_message(
              "An error occurred while feeding your pet (check your pet's name).",
              ephemeral=True,
            )
          print(f"Error: {e}")
          self.session.rollback()

    @app_commands.command(name="buytreats")
    async def get_treats(self, interaction: Interaction):
        """Get treats for your pet"""
        try:
            owned_pet = (
                self.session.query(Pet)
                .filter(Pet.discord_id == interaction.user.id)
                .first()
            )
            if not owned_pet:
                await interaction.response.send_message(
                    "You don't have a pet! Use `/newpet <pet_name>` to create one."
                )
                return
            quantity = random.randint(1, 10)
            owned_pet.treat_count += quantity
            self.session.commit()
            await interaction.response.send_message(
                f"You bought **{quantity}** treat{'s' if quantity > 1 else ''} for **{str(owned_pet.pet_name).capitalize()}**! <:wiseoldman:1147920787471347732>"
              )
        except Exception as e:
          await interaction.response.send_message(
              "An error occurred while getting treats for your pet (check your pet's name).",
              ephemeral=True,
          )
          print(f"Error: {e}")
          self.session.rollback()

    @app_commands.command(name="pethunger")
    async def check_hunger(self, interaction: Interaction):
        """Check your pet's hunger"""
        try:
            owned_pet = (
                self.session.query(Pet)
                .filter(Pet.discord_id == interaction.user.id)
                .first()
            )
            if not owned_pet:
                await interaction.response.send_message(
                    "You don't have a pet! Use `/newpet <pet_name>` to create one."
                )
                return
            await interaction.response.send_message(
                f"Your pet, **{str(owned_pet.pet_name).capitalize()}** is at **{owned_pet.hunger}** hunger! <:wiseoldman:1147920787471347732>"
            )
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while checking your pet's hunger.", ephemeral=True
            )
            print(f"Error: {e}")
            self.session.rollback()

    @app_commands.command(name="treatcount")
    async def check_treats(self, interaction: Interaction):
        """Check your pet's treats"""
        try:
            owned_pet = (
                self.session.query(Pet)
                .filter(Pet.discord_id == interaction.user.id)
                .first()
            )
            if not owned_pet:
                await interaction.response.send_message(
                    "You don't have a pet! Use `/newpet <pet_name>` to create one."
                )
                return
            await interaction.response.send_message(
                f"Your pet, **{str(owned_pet.pet_name).capitalize()}** has **{owned_pet.treat_count}** treat{'s' if owned_pet.treat_count > 1 else ''}! <:wiseoldman:1147920787471347732>"
            )
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while checking your pet's treats.", ephemeral=True
            )
            print(f"Error: {e}")
            self.session.rollback()

    @app_commands.command(name="petinfo")
    async def get_all_info(self, interaction: Interaction):
        """Get info about your pet!"""
        try:
            owned_pet = (
                self.session.query(Pet)
                .filter(Pet.discord_id == interaction.user.id)
                .all()
            )
            embed = Embed(
                title="Pet Information <:catboypepe:1146225949315182612>", color=0x00FF00
            )
            if not owned_pet:
                embed.add_field(
                    name="No Pet <:susspongebob:1145087128087302164>",
                    value="You don't have a pet! Use `/newpet <pet_name>` to create one.",
                    inline=False,
                )
                await interaction.response.send_message(embed=embed)
                return
            for pet in owned_pet:
                embed.add_field(
                    name=f"{str(pet.pet_name).capitalize()}",
                    value=f"Hunger: **{pet.hunger}** | Treats: **{pet.treat_count}** | Happiness: **{pet.happiness}**",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while getting all pets.", ephemeral=True
            )
            print(f"Error: {e}")
            self.session.rollback()


async def setup(client: commands.Bot):
    await client.add_cog(Pets(client))
