from fastapi import Request, Form, HTTPException, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from models import Post, Comment, Like
from deps import SessionDep, CurrentUserDep, templates, PostDep



# app = FastAPI()
router = APIRouter()

# @router을 @router로 바꿈

@router.get('/posts')
def post_list(
  request: Request,
  # db: SessionDep,
  db: SessionDep,
  user: CurrentUserDep
):
  # with Session(engine) as db:

  liked_ids = []
  if user:
    # liked_ids = db.scalars( select(Like.post_id).where(user.id == Like.user_id) ).all()

    # user.likes => select(Like).where(user.id == Like.user_id)
    liked_ids = [like.post_id for like in user.likes ]

  # posts = db.scalars(select(Post)).all() # 전체 게시물 가지고 오는 코드 (정렬 X)
  posts = db.scalars(select(Post).order_by(Post.create_at.desc())).all() # (정렬 O)
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts, 'user': user, 'liked_ids': liked_ids}
  )


@router.get('/posts/new')
def post_new(
  request: Request,
  user: CurrentUserDep
):
  # 로그인을 하지 않은 사람이라면
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  return templates.TemplateResponse(
    request=request,
    name='new.html',
    context={'user': user}
    )

@router.post('/posts/create')
def post_create(
  db: SessionDep,
  user: CurrentUserDep,
  content: str = Form()
):
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  post = Post(content=content, user=user) #user=user 추가함
  db.add(post)
  db.commit()
  # from fastapi.responses import RedirectResponse
  return RedirectResponse('/posts', status_code=303)

@router.get('/posts/{post_id}')
def post_detail(request: Request, post: PostDep, user: CurrentUserDep):

  print(post.comments)

  return templates.TemplateResponse(
    request=request,
    name='detail.html',
    context={'post': post, 'user': user}
  )

@router.get('/posts/{post_id}/edit')
def post_edit(request: Request, post: PostDep, user: CurrentUserDep):
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

@router.post('/posts/{post_id}/update')
def post_update(
  post: PostDep,
  db: SessionDep,
  user: CurrentUserDep,
  content: str = Form()
):
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 게시물 작성자와 로그인한 사람 비교
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='내 글만 수정할 수 있습니다.')

  post.content = content
  db.commit()

  return RedirectResponse('/posts', status_code=303)

@router.post('/posts/{post_id}/delete')
def post_delete(
  post: PostDep,
  db: SessionDep,
  user: CurrentUserDep
):
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 게시물 작성자와 로그인한 사람 비교
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='내 글만 수정할 수 있습니다.')
  
  db.delete(post)
  db.commit()
  return RedirectResponse('/posts', status_code=303)


@router.post('/posts/{post_id}/comments/create')
def comment_create(
  post: PostDep,
  db: SessionDep,
  user: CurrentUserDep, # 1. 현재 로그인한 사람이 들어 있음
  content: str = Form()
):
  # 3. 노파심에 유저가 로그인 안 했으면 밑에 있는 로직 튕기게 추가
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  comment = Comment(content=content, post=post, user=user) # 2.user=user 추가함
  db.add(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post.id}', status_code=303)

@router.post('/posts/{post_id}/comments/{comment_id}/delete')
def comment_delete(
  post_id: int,
  comment_id: int, 
  db: SessionDep,
  user: CurrentUserDep
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



@router.post('/posts/{post_id}/likes')
def post_like(
  post: PostDep,
  db: SessionDep,
  user: CurrentUserDep
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