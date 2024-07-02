# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Any
from datetime import datetime
import os
from dotenv import load_dotenv
from Config.config import settings


load_dotenv(dotenv_path='Config/app.env')
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

#SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL


engine = create_engine(SQLALCHEMY_DATABASE_URL)
#print("engine: ", engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    db = SessionLocal()
    #print("db -> ", db)
    try:
        yield db
    finally:
        db.close()

# @as_declarative()
# class Base_:
#     id: Any
#     __name__: str

#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()

#     # Default fields
#     created_at: datetime
#     updated_at: datetime


