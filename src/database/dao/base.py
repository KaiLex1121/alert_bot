from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import Base

Model = TypeVar("Model", bound=Base)


class BaseDAO(Generic[Model]):
    def __init__(self, model: Type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    def get_by_id(self, id: Any) -> Optional[Model]:
        return self.db_session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Model]:

        stmt = select(self.model).offset(skip).limit(limit)
        result = self.db_session.execute(stmt)
        return result.scalars().all()

    def create(self, obj: Model):
        object = self.session.add(obj)
        return object

    def update(self, db_obj: Model, update_data: dict) -> None:
        for key, value in update_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
            else:
                self.logger.warning(
                    f"Attribute '{key}' not found in model {self.model.__name__} during update."
                )
        self.db_session.add(db_obj)
        return db_obj

    def delete(self, db_obj: Model) -> None:
        self.db_session.delete(db_obj)

    async def flush(self, *objects):
        await self.session.flush(objects)

    async def count(self):
        result = await self.session.execute(select(func.count(self.model.id)))
        return result.scalar_one()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
