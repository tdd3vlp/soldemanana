from typing import Any, Generic, TypeVar
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, pk: Any) -> ModelT | None:
        return await self.session.get(self.model, pk)

    async def get_all(self) -> list[ModelT]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, pk: Any, **kwargs: Any) -> ModelT | None:
        await self.session.execute(
            update(self.model).where(self.model.id == pk).values(**kwargs)
        )
        return await self.get_by_id(pk)

    async def delete(self, pk: Any) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == pk))

    async def save(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
