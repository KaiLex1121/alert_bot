import logging
from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.base import Base

logger = logging.getLogger(__name__)

Model = TypeVar("Model", bound=Base)


class BaseDAO(Generic[Model]):
    def __init__(self, model: Type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id_: Any) -> Optional[Model]:
        return await self.session.get(self.model, id_)

    async def get_all(self, skip: int = 0) -> List[Model]:

        stmt = select(self.model).offset(skip)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj: Model):
        self.session.add(obj)
        await self.flush()
        await self.refresh(obj)
        return obj

    async def update(self, db_obj: Model, update_data: dict) -> None:

        for key, value in update_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
            else:
                logger.warning(
                    f"Attribute '{key}' not found in model {self.model.__name__} during update."
                )
        self.session.add(db_obj)
        await self.flush()
        await self.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Model) -> None:
        await self.session.delete(db_obj)

    async def flush(self, *objects: Sequence[Any] | None) -> None:
        await self.session.flush(*objects)

    async def count(self):
        result = await self.session.execute(select(func.count(self.model.id)))
        return result.scalar_one()

    async def refresh(self, *objects) -> None:
        await self.session.refresh(*objects)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
