from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models.pet import Pet



class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def add_new_user_pet(self, discord_id: int, pet_name: str):
       new_user = Pet(owner_id=discord_id, pet_name=pet_name)
       self.db_session.add(new_user)
       await self.db_session.flush()
       query = await self.db_session.execute(
           select(Pet).order_by(Pet.id)
           )
       return query.scalars().all()
    
    async def get_user_pet(self, discord_id: int):
        """
        The get_user_pet function is used to retrieve a user's pet from the database.
        It takes in a discord_id and returns the first result of that query.
        
        :param self: Represent the instance of the class
        :param discord_id: int: Specify the discord id of the user we want to get their pet
        :return: The first result from the query
        :doc-author: Trelent
        """
        query = await self.db_session.execute(
            select(Pet).where(Pet.owner_id == discord_id)
            )
        return query.scalars().first()
    
    async def get_all_pets(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.id)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_hunger(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.hunger)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_happiness(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.happiness)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_treat_count(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.treat_count)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_owner_id(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.owner_id)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_pet_name(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.pet_name)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_id(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.id)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_owner_id(self):
        query = await self.db_session.execute(
            select(Pet).order_by(Pet.owner_id)
            )
        return query.scalars().all()
    
    