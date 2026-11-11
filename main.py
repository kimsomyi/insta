from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, select, func, ForeignKey
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
from pwdlib import PasswordHash
import secrets

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
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship(back_populates='posts')

class Comment(Base):
  __tablename__ = 'comments'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  create_at: Mapped[datetime] = mapped_column(server_default=func.now())

  # Post (1) : Comment (N) 관계 설정
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
  post: Mapped['Post'] = relationship(back_populates='comments')

  # User(1) : Comment (N) 관계 설정
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship()

class User(Base):
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(unique=True)
  password_hash: Mapped[str]
  posts: Mapped[list['Post']] = relationship(back_populates='user')
  # commets: Mapped[list['Post']] = relationship(back_populates='user') 유저가 작성한 댓글만 모아서 보여 줄 필요성은 없어서 주석처리 하고 Comment 클래스에서만 user 관계

# 어떤 유저의 신분증을 보관하는 장소
class UserSession(Base):
  __tablename__ = 'sessions' # db 테이블 이름

  # id = 신분증
  id: Mapped[str] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  user: Mapped['User'] = relationship() # User 클래스를 1:1로 설정하겠다
  # 이 신분증을 통해서 조회하기 위해서 일방향으로 설정함

class Like(Base):
  __tablename__ = 'likes'

  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'), primary_key=True)

# 전역처리
app = FastAPI()
templates = Jinja2Templates(directory='templates')
password_hash = PasswordHash.recommended()


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


def get_current_user(request: Request, db: Session = Depends(get_db)):
  session_id = request.cookies.get('session_id')

  # 신분증 유무 판단
  if session_id is None:
    return None

  user_session = db.get(UserSession, session_id)

  # 신분증 유효한지 검사
  if user_session is None:
    return None

  return user_session.user

@app.get('/')
def home():
  return {'hi': 'hello'}


@app.get('/posts')
def post_list(
  request: Request,
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  # with Session(engine) as db:

  # posts = db.scalars(select(Post)).all() # 전체 게시물 가지고 오는 코드 (정렬 X)
  posts = db.scalars(select(Post).order_by(Post.create_at.desc())).all() # (정렬 O)
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts, 'user': user }
  )


@app.get('/posts/new')
def post_new(
  request: Request,
  user: User | None = Depends(get_current_user)
):
  # 로그인을 하지 않은 사람이라면
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  return templates.TemplateResponse(
    request=request,
    name='new.html',
    context={'user': user}
    )

@app.post('/posts/create')
def post_create(content: str = Form(), db: Session = Depends(get_db), user: User | None = Depends(get_current_user)):
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  post = Post(content=content, user=user) #user=user 추가함
  db.add(post)
  db.commit()
  # from fastapi.responses import RedirectResponse
  return RedirectResponse('/posts', status_code=303)

@app.get('/posts/{post_id}')
def post_detail(request: Request, post: Post = Depends(get_post_or_404), user: User | None = Depends(get_current_user)):

  print(post.comments)

  return templates.TemplateResponse(
    request=request,
    name='detail.html',
    context={'post': post, 'user': user}
  )

@app.get('/posts/{post_id}/edit')
def post_edit(request: Request, post: Post = Depends(get_post_or_404), user: User | None = Depends(get_current_user)):
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 게시물 작성자와 로그인한 사람 비교
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='내 글만 수정할 수 있습니다.')

  return templates.TemplateResponse(
    request=request,
    name='edit.html',
    context={'post': post, 'user': user}
  )

@app.post('/posts/{post_id}/update')
def post_update(
  content: str = Form(),
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 게시물 작성자와 로그인한 사람 비교
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='내 글만 수정할 수 있습니다.')

  post.content = content
  db.commit()

  return RedirectResponse('/posts', status_code=303)

@app.post('/posts/{post_id}/delete')
def post_delete(
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 게시물 작성자와 로그인한 사람 비교
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='내 글만 수정할 수 있습니다.')
  
  db.delete(post)
  db.commit()
  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/comments/create')
def comment_create(
  content: str = Form(),
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user) # 1. 현재 로그인한 사람이 들어 있음
):
  # 3. 노파심에 유저가 로그인 안 했으면 밑에 있는 로직 튕기게 추가
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  comment = Comment(content=content, post=post, user=user) # 2.user=user 추가함
  db.add(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post.id}', status_code=303)

@app.post('/posts/{post_id}/comments/{comment_id}/delete')
def comment_delete(
  post_id: int,
  comment_id: int, 
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  # 로그인 안 한 사람
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 내가 쓴 댓글인지
  comment = db.get(Comment, comment_id)
  if comment.user_id != user.id:
    raise HTTPException(status_code=403, detail='내 댓글만 삭제 가능') #403=권한없음

  # 댓글이 아예 없으면
  if comment is None:
    raise HTTPException(status_code=404, detail='해당 댓글이 없습니다.')

  db.delete(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post_id}', status_code=303)


# a태그를 통해서 들어오는 signup
@app.get('/signup')
def signup_form(request: Request, user: User | None = Depends(get_current_user)):
  return templates.TemplateResponse(
    request=request,
    name='signup.html',
    context={'user': user}
  )


# form method = 'post' 방식으로 들어오는 signup
@app.post('/signup')
def signup(
  request: Request,
  username: str = Form(),
  password: str = Form(),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):

  # 이미 있는 유저인지 검증
  # SELECT * FROM users WHERE username = 'somyi'
  exists = db.scalar(select(User).where(User.username == username))

  # 이미 유저네임을 사용하는 경우
  if exists:
    return templates.TemplateResponse(
      request=request,
      name='signup.html',
      context={'error': '이미 있는 아이디입니다.'}
    )


  # User(username=username, password_hash=password) 얘는 평문으로 저장됨

  # password 암호화 
  # password_hash = PasswordHash.recommended() <- 얘는 위에 올려서 전역 처리함. 다른 곳에서도 쓸 거임
  hashed_pw = password_hash.hash(password)

  user = User(username=username, password_hash=hashed_pw)
  db.add(user)
  db.commit()

  return RedirectResponse('/login', status_code=303)




# 하나는 아이디와 패스워드를 입력하는 종이

@app.get('/login')
def login_form(request: Request, user: User | None = Depends(get_current_user)):
  return templates.TemplateResponse(
    request=request,
    name='login.html',
    context={'user': user}
  )

# 사용자가 데이터를 입력했을 때 그걸 처리함

@app.post('/login')
def login(
  request: Request,
  username: str = Form(),
  password: str = Form(),
  db: Session = Depends(get_db)
):
  # 방금 입력한 아이디에 해당하는 유저 찾기
  user = db.scalar(select(User).where(User.username == username))

  # password_hash.verify(password, user.password_hash)

  # 유저가 존재하지 않을 때 or 그 유저의 비밀번호와 방금 입력한 비밀번호가 다른 경우 => 에러입니다
  if (user is None) or not (password_hash.verify(password, user.password_hash)):
    return templates.TemplateResponse(
      request=request,
      name='login.html',
      context={'error': '아이디가 존재하지 않습니다.'}
    )

  # 비밀번호가 일치하면 => 신분증 발행 
  session_id = secrets.token_urlsafe(32) # 랜덤으로 문자열을 넣어 주는데, 문자열에 넣어도 문제 없는 생성기
  # 발행한 신분증을 DB에 저장
  user_session = UserSession(id=session_id, user=user)
  db.add(user_session)
  db.commit()

  # 신분증을 유저한테 전달 (쿠키에 저장시키기)
  response = RedirectResponse('/posts', status_code=303)
  response.set_cookie('session_id', session_id, httponly=True, samesite='lax')
  return response

@app.post('/logout')
def logout(request: Request, db: Session = Depends(get_db)):
  # 신분증 정보 가져오기
  session_id = request.cookies.get('session_id')
  user_session = db.get(UserSession, session_id)

  if user_session:
    db.delete(user_session)
    db.commit()

  response = RedirectResponse('/posts', status_code=303)
  response.delete_cookie('session_id')
  return response


@app.post('/posts/{post_id}/likes')
def post_like(
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # like가 이미 있는지?
  result = db.get(Like, (user.id, post.id))

  if result:
    # 좋아요가 이미 눌린 경우
    db.delete(result)
  else:
    # 아직 좋아요 안 누른 경우
    like = Like(user_id=user.id, post_id=post.id)
    db.add(like)
    
  db.commit()

  return RedirectResponse('/posts', status_code=303)