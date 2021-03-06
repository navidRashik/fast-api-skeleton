from common.dependencies import get_token_header
from fastapi import APIRouter, Depends
from fastapi import APIRouter
from fastapi import Depends, FastAPI
from sqlalchemy.sql.sqltypes import Integer, String

import databases
import sqlalchemy
from fastapi import FastAPI
from sqlalchemy.dialects.postgresql import ARRAY
import glob
from common.dependencies import get_query_token, get_token_header
# from .internal import admin
# from apps import items, user

import importlib.util
import logging
# SQLAlchemy specific code, as with any other app
# DATABASE_URL = "sqlite:///./test.db"
DATABASE_URL = "postgresql://user:password@db:5432/db"

# DATABASE_URL = "postgresql://user:password@localhost:5432/db"
secret_key = "A-big-secret-key"
secret_algorithm = "HS256"
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    sqlalchemy.Column("hash_password", sqlalchemy.String),
    sqlalchemy.Column("tags", ARRAY(String)),
    sqlalchemy.Column("tags_expire_at", sqlalchemy.DateTime, nullable=True)
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={
        # "check_same_thread": False,
    }
)
metadata.create_all(engine)

app = FastAPI(dependencies=[Depends(get_query_token)])

@app.get("/")
async def root():
    return {"message": "Health is Ok"}


@app.on_event("startup")
async def handle_startup():
    await database.connect()
    router_list = list()
    for file_name in glob.iglob('./**/routers.py', recursive=True):
        print('-----------------loop')
        print(file_name)
        spec = importlib.util.spec_from_file_location('routers', file_name)
        each_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(each_app)
        router_list += each_app.routers
        print(router_list)

    for rt in router_list:
        print(rt)
        app.include_router(rt)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()