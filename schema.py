from model import User, Entity
from database import DatabaseHandler
import strawberry
import typing
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv


db: DatabaseHandler = None


def copyFields(src, dst):
    for key, value in src.__dict__.items():
        if key in dst.__dict__:
            setattr(dst, key, value)


@strawberry.input
class EditEntityInput:
    user_id: typing.Optional[str] = None
    description: typing.Optional[str] = None
    type: typing.Optional[str] = None
    status: typing.Optional[str] = "created"


@strawberry.input
class TimestampFilterInput:
    filter_type: str
    sign: str
    timestamp: datetime


@strawberry.type
class Query:

    @strawberry.field
    async def entities(self, uid: typing.Optional[str] = None, timestamp_filter: typing.Optional[TimestampFilterInput] = None, type: typing.Optional[str] = None, status: typing.Optional[str] = None,) -> typing.List[Entity] | None:
        if status is not None and status not in ("created", "deleted"):
            raise ValueError("status should be 'created' or 'deleted'")
        query_statement = (Entity.uid == uid if uid is not None else True) and \
                          (Entity.type == type if type is not None else True) and \
                          (Entity.status == status if status is not None else True)

        if timestamp_filter is not None:
            if timestamp_filter.filter_type == "created_at":
                match timestamp_filter.sign:
                    case "<":
                        query_statement = query_statement and Entity.created_at < timestamp_filter.timestamp
                    case ">":
                        query_statement = query_statement and Entity.created_at > timestamp_filter.timestamp
                    case "==":
                        query_statement = query_statement.filter and Entity.created_at == timestamp_filter.timestamp
                    case _:
                        raise ValueError("Sign should be '<', '>' or '=='")
            elif timestamp_filter.filter_type == "updated_at":
                match timestamp_filter.sign:
                    case "<":
                        query_statement = query_statement and Entity.updated_at < timestamp_filter.timestamp
                    case ">":
                        query_statement = query_statement and Entity.updated_at > timestamp_filter.timestamp
                    case "==":
                        query_statement = query_statement and Entity.updated_at == timestamp_filter.timestamp
                    case _:
                        raise ValueError("Sign should be '<', '>' or '=='")
            else:
                raise ValueError(
                    "filter_type should be 'created_at' or 'updated_at'")

        query_answer = await db.selectQuery(Entity, query_statement)
        return query_answer
    

    @strawberry.field
    async def users(self) -> typing.List[User] | None:
        users = await db.selectQuery(User)
        return users


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def edit_entity(self, uid: str, data: EditEntityInput) -> str:
        entity = await db.selectQuery(
            Entity, Entity.uid == uid, return_first=True)
        if entity is None:
            raise ValueError("no entity with such uid")
        if data.user_id is not None:
            user = await db.selectQuery(User, User.id == data.user_id, return_first=True)
            if user is None:
                raise ValueError("no user with such id")
        if data.status is not None and data.status not in ("created", "deleted"):
            raise ValueError("status should be 'created' or 'deleted'")
        copyFields(data, entity)
        await db.commit()
        print(f'mutation at uid "{uid}", data: {data}')
        return "ok"

schema = strawberry.Schema(query=Query, mutation=Mutation)


async def main():
    global db
    if os.path.exists(os.path.join(os.path.dirname(__file__), '.env')):
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    PG_USERNAME = os.environ.get('PG_USERNAME')
    PG_PASSWORD = os.environ.get('PG_PASSWORD')
    PG_DATABASE = os.environ.get('PG_DATABASE')
    PG_HOST = os.environ.get('PG_HOST')
    db = await DatabaseHandler().create(f'postgresql+asyncpg://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}/{PG_DATABASE}')

    
asyncio.get_event_loop().create_task(main())
