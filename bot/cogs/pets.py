import datetime
import random

from discord import Interaction, app_commands
from discord.ext import commands, tasks
from models.db import Base
from models.pet import Pet
from sqlalchemy.future import select


class Pets(commands.Cog, name="Pets"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.remove_hunger.start()
        self.update_happiness.start()
        self.init_database.start()
        self.get_pets.start()
        self.pets = []

    @tasks.loop(count=1)
    async def init_database(self):
        async with self.client.engine.begin() as session:
            await session.run_sync(Base.metadata.create_all)

    @tasks.loop(minutes=1)
    async def get_pets(self):
        async with self.client.async_session() as session:
            query = await session.execute(select(Pet))
            self.pets = query.scalars().all()

    @tasks.loop(minutes=30)
    async def remove_hunger(self):
        async with self.client.async_session() as session:
            for pet in self.pets:
                pet.hunger -= 1
                try:
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()

    @tasks.loop(minutes=120)
    async def update_happiness(self):
        async with self.client.async_session() as session:
            for pet in self.pets:
                if pet.hunger > 5:
                    pet.happiness += 1
                else:
                    pet.happiness -= 1
                try:
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()

    @app_commands.command(name="newpet")
    async def create(self, interaction: Interaction, pet_name: str):
        """Create a new pet"""
        with self.client.async_session() as session:
            query = await session.execute(
                select(Pet).filter(Pet.discord_id == interaction.user.id)
            )
            existing_pet = query.scalar_one_or_none()
            if existing_pet:
                await interaction.response.send_message(
                    f"You already have a pet named {existing_pet.pet_name}! Use `/givetreat` to feed it. <:susspongebob:1145087128087302164>"
                )
            else:
                pet = Pet(
                    discord_id=interaction.user.id,
                    pet_name=pet_name,
                    hunger=50,
                    treat_count=20,
                    happiness=50,
                    last_fed=datetime.datetime.utcnow(),
                )
                try:
                    session.add(pet)
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    self.client.log.error(e)
                    session.rollback()
                await interaction.response.send_message(
                    f"Your pet **{str(pet_name).capitalize()}** has been created! <:wiseoldman:1147920787471347732>"
                )
                self.client.log.info(
                    f"User {interaction.user} created a pet named {pet_name}."
                )

    @app_commands.command(name="givetreat")
    async def feed(self, interaction: Interaction):
        """Feed your pet"""
        with self.client.async_session() as session:
            query = await session.execute(
                select(Pet).filter(Pet.discord_id == interaction.user.id)
            )
            owned_pet = query.scalar_one_or_none()
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
            owned_pet.last_fed = datetime.datetime.utcnow()
            try:
                await session.flush()
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()
            await interaction.response.send_message(
                f"Your pet **{str(owned_pet.pet_name).capitalize()}** has been fed **{quantity}** treat{'s' if quantity > 1 else ''}! <:wiseoldman:1147920787471347732>"
            )

    @app_commands.command(name="buytreats")
    async def get_treats(self, interaction: Interaction):
        """Get treats for your pet"""
        async with self.client.async_session() as session:
            query = await session.execute(
                select(Pet).filter(Pet.discord_id == interaction.user.id)
            )
            owned_pet = query.scalar_one_or_none()
            if not owned_pet:
                await interaction.response.send_message(
                    "You don't have a pet! Use `/newpet <pet_name>` to create one."
                )
                return
            quantity = random.randint(1, 10)
            owned_pet.treat_count += quantity
            try:
                await session.flush()
                await session.commit()
            except Exception as e:
                self.client.log.error(e)
                await session.rollback()
            await interaction.response.send_message(
                f"You bought **{quantity}** treat{'s' if quantity > 1 else ''} for **{str(owned_pet.pet_name).capitalize()}**! <:wiseoldman:1147920787471347732>"
            )

    @app_commands.command(name="pethunger")
    async def check_hunger(self, interaction: Interaction):
        """Check your pet's hunger"""
        async with self.client.async_session() as session:
            query = await session.execute(
                select(Pet).filter(Pet.discord_id == interaction.user.id)
            )
            owned_pet = query.scalar_one_or_none()
            if not owned_pet:
                await interaction.response.send_message(
                    "You don't have a pet! Use `/newpet <pet_name>` to create one."
                )
                return
            await interaction.response.send_message(
                f"Your pet, **{str(owned_pet.pet_name).capitalize()}** is at **{owned_pet.hunger}** hunger! <:wiseoldman:1147920787471347732>"
            )

    @app_commands.command(name="treatcount")
    async def check_treats(self, interaction: Interaction):
        """Check your pet's treats"""
        async with self.client.async_session() as session:
            query = await session.execute(
                select(Pet).filter(Pet.discord_id == interaction.user.id)
            )
            owned_pet = query.scalar_one_or_none()
            if not owned_pet:
                await interaction.response.send_message(
                    "You don't have a pet! Use `/newpet <pet_name>` to create one."
                )
                return
            await interaction.response.send_message(
                f"Your pet, **{str(owned_pet.pet_name).capitalize()}** has **{owned_pet.treat_count}** treat{'s' if owned_pet.treat_count > 1 else ''}! <:wiseoldman:1147920787471347732>"
            )


async def setup(client: commands.Bot):
    await client.add_cog(Pets(client))
