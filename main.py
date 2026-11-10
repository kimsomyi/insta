from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, select, func, ForeignKey
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일의 값을 읽어 옴
DB_URL = os.environ['DB_URL']
engine = create_engine(DB_URL, echo=True)

# 모델 정의
class Base(DeclarativeBase):
  pass

class Post(Base):
  __tablename__ = 'posts'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  create_at: Mapped[datetime] = mapped_column(server_default=func.now())
  comments: Mapped[list['Comment']] = relationship(
    back_populates='post',
    cascade='all, delete-orphan'
    )


class Comment(Base):
  __tablename__ = 'comments'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  create_at: Mapped[datetime] = mapped_column(server_default=func.now())
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
  post: Mapped['Post'] = relationship(back_populates='comments')

app = FastAPI()
templates = Jinja2Templates(directory='templates')

class User(Base):
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(unique=True)
  password_hash: Mapped[str]





def get_db():
  with Session(engine) as db:
    yield db 


# 해당 함수를 실행하기 위해서 get_db를 종속성 걸어 줌
def get_post_or_404(post_id: int, db: Session = Depends(get_db)):
  post = db.get(Post, post_id)

  if post is None:
    # from fastapi import HTTPException
    raise HTTPException(status_code=404, detail='해당 게시물이 없습니다.')
  
  return post

@app.get('/')
def home():
  return {'hi': 'hello'}


@app.get('/posts')
def post_list(request: Request, db: Session = Depends(get_db)):
  # with Session(engine) as db:

  # posts = db.scalars(select(Post)).all() # 전체 게시물 가지고 오는 코드 (정렬 X)
  posts = db.scalars(select(Post).order_by(Post.create_at.desc())).all() # (정렬 O)
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts}
  )


@app.get('/posts/new')
def post_new(request: Request):
  return templates.TemplateResponse(
    request=request,
    name='new.html'
  )

@app.post('/posts/create')
def post_create(content: str = Form(), db: Session = Depends(get_db)):
  post = Post(content=content)
  db.add(post)
  db.commit()
  # from fastapi.responses import RedirectResponse
  return RedirectResponse('/posts', status_code=303)

@app.get('/posts/{post_id}')
def post_detail(request: Request, post: Post = Depends(get_post_or_404)):

  print(post.comments)

  return templates.TemplateResponse(
    request=request,
    name='detail.html',
    context={'post': post}
  )

@app.get('/posts/{post_id}/edit')
def post_edit(request: Request, post: Post = Depends(get_post_or_404)):
  return templates.TemplateResponse(
    request=request,
    name='edit.html',
    context={'post': post}
  )

@app.post('/posts/{post_id}/update')
def post_update(
  content: str = Form(),
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  post.content = content
  db.commit()

  return RedirectResponse('/posts', status_code=303)

@app.post('/posts/{post_id}/delete')
def post_delete(
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  db.delete(post)
  db.commit()
  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/comments/create')
def comment_create(
  content: str = Form(),
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  comment = Comment(content=content, post=post)
  db.add(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post.id}', status_code=303)

@app.post('/posts/{post_id}/comments/{comment_id}/delete')
def comment_delete(post_id: int, comment_id: int, db: Session = Depends(get_db)):
  comment = db.get(Comment, comment_id)

  if comment is None:
    raise HTTPException(status_code=404, detail='해당 댓글이 없습니다.')

  db.delete(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post_id}', status_code=303)


# a태그를 통해서 들어오는 signup
@app.get('/signup')
def signup_form(request: Request):
  return templates.TemplateResponse(
    request=request,
    name='signup.html'
  )


# form method = 'post' 방식으로 들어오는 signup
@app.post('/signup')
def signup():
  pass