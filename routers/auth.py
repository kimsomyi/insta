from fastapi import Request, Form, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy import select
import secrets

from deps import templates, password_hash, CurrentUserDep, SessionDep
from models import User, UserSession


router = APIRouter()

# a태그를 통해서 들어오는 signup
@router.get('/signup')
def signup_form(request: Request, user: CurrentUserDep):
  return templates.TemplateResponse(
    request=request,
    name='signup.html',
    context={'user': user}
  )


# form method = 'post' 방식으로 들어오는 signup
@router.post('/signup')
def signup(
  request: Request,
  db: SessionDep,
  user: CurrentUserDep,
  username: str = Form(),
  password: str = Form()
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

@router.get('/login')
def login_form(request: Request, user: CurrentUserDep):
  return templates.TemplateResponse(
    request=request,
    name='login.html',
    context={'user': user}
  )

# 사용자가 데이터를 입력했을 때 그걸 처리함

@router.post('/login')
def login(
  request: Request,
  db: SessionDep,
  username: str = Form(),
  password: str = Form()
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

@router.post('/logout')
def logout(request: Request, db: SessionDep):
  # 신분증 정보 가져오기
  session_id = request.cookies.get('session_id')
  user_session = db.get(UserSession, session_id)

  if user_session:
    db.delete(user_session)
    db.commit()

  response = RedirectResponse('/posts', status_code=303)
  response.delete_cookie('session_id')
  return response