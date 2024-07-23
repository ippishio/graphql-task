from model import Entity, User
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Table, Column, String, DateTime, ForeignKey, Engine
from sqlalchemy.orm import registry, relationship
from sqlalchemy.future import select
from sqlalchemy import exc


class DatabaseHandler:

    engine: Engine
    session: AsyncSession
    users_table: Table
    entities_table: Table
    mapper_registry = registry()

    async def create(self, url: String):
        self = DatabaseHandler()
        self.engine = create_async_engine(url, echo=True)
        self.users_table = Table('users', self.mapper_registry.metadata,
                                 Column('id', String(64), primary_key=True),
                                 Column('username', String(64)),
                                 quote=False
                                 )
        self.entities_table = Table('entities', self.mapper_registry.metadata,
                                    Column('uid', String(64),
                                           primary_key=True),
                                    Column('created_at', DateTime(timezone=True),
                                           default=datetime.now()),
                                    Column('updated_at', DateTime(timezone=True),
                                           default=datetime.now(), onupdate=datetime.now()),
                                    # Column('user_id', String(64), ForeignKey(User.id)),
                                    Column('user_id', String(64),
                                           ForeignKey("users.id")),
                                    Column('description', String(256)),
                                    Column('type', String(16)),
                                    Column('status', String(16)),
                                    quote=False
                                    )
        self.mapper_registry.map_imperatively(User, self.users_table)
        self.mapper_registry.map_imperatively(Entity, self.entities_table, properties={
            "foreign": relationship(User)
        })
        async with self.engine.begin() as conn:
            await conn.run_sync(self.mapper_registry.metadata.create_all)
        self.session = AsyncSession(self.engine, expire_on_commit=False)
        return self

    async def execute(self, statement):
        try:
            return await self.session.execute(statement)
        except exc.SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(
                "Database error, current transaction rolled back", e)

    async def commit(self):
        try:
            await self.session.commit()
        except exc.SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(
                "Database error, current transaction rolled back", e)

    async def selectQuery(self, entity: any, condition: bool = True, return_first: bool = False):
        statement = select(entity).where(condition)
        result = await self.execute(statement)
        if return_first:
            return result.scalar()
        return result.scalars()

    async def insertQuery(self, *entities: any):
        if len(entities) == 0:
            return
        self.session.add_all(entities)
        self.commit()
