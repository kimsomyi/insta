from fastapi import APIRouter, Request, HTTPException
from deps import templates, SessionDep, CurrentUserDep
from sqlalchemy import select
from models import User, Post

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
    posts = db.scalars( select(Post).where(Post.user_id == owner.id).order_by(Post.create_at.desc()) ).all()

    return templates.TemplateResponse(
        request=request,
        name='profile.html',
        context={
            'owner': owner,
            'posts': posts,
            'user': user
        }

    )