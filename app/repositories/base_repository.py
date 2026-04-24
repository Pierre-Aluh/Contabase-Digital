"""Repositorio base com operacoes CRUD genericas."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model_cls):
        self.session = session
        self.model_cls = model_cls

    def create(self, data: dict) -> ModelType:
        entity = self.model_cls(**data)
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: int) -> ModelType | None:
        return self.session.get(self.model_cls, entity_id)

    def list_all(self) -> list[ModelType]:
        return list(self.session.execute(select(self.model_cls)).scalars().all())

    def update(self, entity: ModelType, data: dict) -> ModelType:
        for field, value in data.items():
            setattr(entity, field, value)
        self.session.flush()
        return entity

    def delete(self, entity: ModelType) -> None:
        self.session.delete(entity)
        self.session.flush()

    def exists(self, **filters) -> bool:
        stmt = select(self.model_cls).filter_by(**filters).limit(1)
        return self.session.execute(stmt).scalar_one_or_none() is not None
