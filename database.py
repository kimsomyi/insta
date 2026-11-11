from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()  # DB_URL을 읽기 전에 .env 파일부터 읽어 옴

DB_URL = os.environ['DB_URL']
engine = create_engine(DB_URL, echo=True)

class Base(DeclarativeBase):
  pass