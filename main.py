from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, select, func, ForeignKey
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
from pwdlib import PasswordHash
import secrets
from typing import Annotated
from routers import posts, auth, users

load_dotenv()  # .env 파일의 값을 읽어 옴
DB_URL = os.environ['DB_URL']
engine = create_engine(DB_URL, echo=True)


# 전역처리
app = FastAPI()

app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(users.router)

# /media/... 주소로 오는 요청을 media 폴더의 실제 파일로 연결
app.mount('/media', StaticFiles(directory='media'), name='media')
app.mount('/static', StaticFiles(directory='static'), name='static')


def get_db():
  with Session(engine) as db:
    yield db 


@app.get('/')
def home():
  return {'hi': 'hello'}






