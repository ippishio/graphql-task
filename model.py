import typing
import strawberry
from datetime import datetime
from dataclasses import dataclass, field
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ARRAY, TIMESTAMP, DateTime, select, ForeignKey
from sqlalchemy.orm import Session, registry, relationship

@strawberry.type
@dataclass
class User:
    id: str = field(default_factory=str)
    username: str = field(default_factory=str)

@strawberry.type
@dataclass
class Entity:
    uid: str = field(default_factory=str)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    user_id: str = field(default_factory=str)
    description: str = field(default_factory=str)

    # состояние сущности, - created, deleted
    type: str = field(default_factory=str)
    status: str = field(default_factory="created")