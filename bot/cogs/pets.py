import os
import random

from discord import Embed, app_commands, Interaction
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
        self.add_treat.start()
        self.remove_hunger.start()

    @tasks.loop(minutes=120)
    async def add_treat(self):
        for pet in self.pets:
            r_treat = random.randint(1, 10)
            pet.treat_count += r_treat
        self.session.commit()

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
                    f"You already have a pet! Use `/pets feed <pet_name>` to feed it. <:susspongebob:1145087128087302164>"
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
    async def feed(self, interaction: Interaction, pet_name: str):
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
            pet = self.session.query(Pet).filter(Pet.pet_name == pet_name).first()
            if pet:
                quantity = random.randint(1, 10)
                if quantity > pet.treat_count:
                    await interaction.response.send_message(
                        f"You don't have enough treats to feed **{str(pet_name).capitalize()}**! <:susspongebob:1145087128087302164>"
                    )
                    return
                pet.hunger += quantity
                self.session.commit()
                await interaction.response.send_message(
                    f"Your pet **{str(pet_name).capitalize()}** has been fed **{quantity}** treat{'s' if quantity > 1 else ''}! <:wiseoldman:1147920787471347732>"
                )
            else:
                await interaction.response.send_message(
                    f"You don't have a pet named **{str(pet_name).capitalize()}**!"
                )
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while feeding your pet (check your pet's name).",
                ephemeral=True,
            )
            print(f"Error: {e}")
            self.session.rollback()

    @app_commands.command(name="checkhunger")
    async def check_hunger(self, interaction: Interaction, pet_name: str):
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
            pet = self.session.query(Pet).filter(Pet.pet_name == pet_name).first()
            if pet:
                await interaction.response.send_message(
                    f"Your pet, **{str(pet_name).capitalize()}** is at **{pet.hunger}** hunger! <:wiseoldman:1147920787471347732>"
                )
            else:
                await interaction.response.send_message(
                    f"You don't have a pet named **{str(pet_name).capitalize()}**! <:susspongebob:1145087128087302164>"
                )
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while checking your pet's hunger.", ephemeral=True
            )
            print(f"Error: {e}")
            self.session.rollback()

    @app_commands.command(name="checktreats")
    async def check_treats(self, interaction: Interaction, pet_name: str):
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
            pet = self.session.query(Pet).filter(Pet.pet_name == pet_name).first()
            if pet:
                await interaction.response.send_message(
                    f"Your pet, **{str(pet_name).capitalize()}** has **{pet.treat_count}** treat{'s' if pet.treat_count > 1 else ''}! <:wiseoldman:1147920787471347732>"
                )
            else:
                await interaction.response.send_message(
                    f"You don't have a pet named **{str(pet_name).capitalize()}**! <:susspongebob:1145087128087302164>"
                )
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while checking your pet's treats.", ephemeral=True
            )
            print(f"Error: {e}")
            self.session.rollback()

    @app_commands.command(name="mypets")
    async def get_all_pets(self, interaction: Interaction):
        """Get all pets"""
        try:
            pets = (
                self.session.query(Pet)
                .filter(Pet.discord_id == interaction.user.id)
                .all()
            )
            embed = Embed(title="All Pets <:catboypepe:1146225949315182612>", color=0x00FF00)
            if not pets:
                embed.add_field(
                    name="No Pets <:susspongebob:1145087128087302164>",
                    value="You don't have any pets! Use `/newpet <pet_name>` to create one.",
                    inline=False,
                )
                await interaction.response.send_message(embed=embed)
                return
            for pet in pets:
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
