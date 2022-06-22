from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import ckan.model as model
from ckan.lib.dictization import table_dictize
from ckan.model.types import make_uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    UnicodeText,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship
from typing_extensions import Self

from .base import Base


class Report(Base):
    __tablename__ = "check_link_report"

    id = Column(UnicodeText, primary_key=True, default=make_uuid)
    url = Column(UnicodeText, primary_key=True, default=make_uuid)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    resource_id = Column(UnicodeText, ForeignKey(model.Resource.id), nullable=True)
    details = Column(JSONB, nullable=False, default=dict)

    resource = relationship(
        model.Resource,
        backref=backref("check_link_report", cascade="all, delete", uselist=False),
    )

    @classmethod
    def by_resource_id(cls, id_: str):
        return model.Session.query(cls).filter(cls.resource_id == id_).one_or_none()

    def dictize(self, context: dict[str, Any]) -> dict[str, Any]:
        result = table_dictize(self, context)

        return result

    @classmethod
    def by_details(cls, path: Iterable[str], value: str) -> Iterable[Self]:
        key: Any = cls.details
        for segment in path:
            key = key[segment]

        return model.Session.query(cls).filter(key.astext == value)
