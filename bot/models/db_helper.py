from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models.cats import Pets



class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def add_new_user_pet(self, discord_id: int, pet_name: str):
       new_user = Pets(owner_id=discord_id, pet_name=pet_name)
       self.db_session.add(new_user)
       await self.db_session.flush()
       query = await self.db_session.execute(
           select(Pets).order_by(Pets.id)
           )
       return query.scalars().all()
    
    async def get_user_pet(self, discord_id: int):
        query = await self.db_session.execute(
            select(Pets).where(Pets.owner_id == discord_id)
            )
        return query.scalars().first()
    
    async def get_all_pets(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.id)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_hunger(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.hunger)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_happiness(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.happiness)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_treat_count(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.treat_count)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_owner_id(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.owner_id)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_pet_name(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.pet_name)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_id(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.id)
            )
        return query.scalars().all()
    
    async def get_all_pets_by_owner_id(self):
        query = await self.db_session.execute(
            select(Pets).order_by(Pets.owner_id)
            )
        return query.scalars().all()
    
    