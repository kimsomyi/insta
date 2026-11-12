from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from deps import templates, SessionDep, CurrentUserDep
from sqlalchemy import select
from models import User, Post, Follow

router = APIRouter()

@router.get('/users/{username}')
def user_profile(
    request: Request,
    username: str,
    db: SessionDep,
    user: CurrentUserDep
):
    # 보려고 하는 프로필 유저 정보
    owner = db.scalar( select(User).where(User.username == username) )
    if owner is None:
        raise HTTPException(status_code=404, detail='해당 사용자가 없습니다.')

    
    # 프로필 유저가 작성한 모든 게시물 찾기
    posts = db.scalars( select(Post).where(Post.user_id == owner.id).order_by(Post.create_at.desc())).all()

    # 해당 프로필에 팔로우가 몇 명인지?
    # follower_list = db.scalars( select(Follow).where(Follow.following_id == owner.id)).all()

    # 해당 프로필에 팔로잉이 몇 명인지?
    # following_list = db.scalars( select(Follow).where(Follow.follower_id == owner.id)).all()

    follow = None
    if user:
        follow = db.get(Follow, (user.id, owner.id))

    return templates.TemplateResponse(
        request=request,
        name='profile.html',
        context={
            'owner': owner,
            'posts': posts,
            'user': user,
            'follow': follow
        }
    )

@router.post('/users/{username}/follows')
def user_follow(
    username: str,
    db: SessionDep,
    user: CurrentUserDep
):
    # 비로그인 유저 로그인 페이지로
    if user is None:
        return RedirectResponse('/login', status_code=303)

    owner = db.scalar( select(User).where(User.username == username) )

    # 이미 팔로우 했는지 조회
    follow = db.scalar(
        select(Follow).where(
            Follow.follower_id == user.id,
            Follow.following_id == owner.id,
        )
    )

    # 값이 있으면 = 팔로우를 헸으면 지우기 = 팔로우 취소
    if follow:
        db.delete(follow)
    else:
        # 팔로우 안 했으면 추가
        follow = Follow(follower_id=user.id, following_id=owner.id)
        db.add(follow)

    db.commit()

    return RedirectResponse(f'/users/{username}', status_code=303)