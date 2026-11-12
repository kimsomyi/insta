from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base



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

  likes: Mapped[list['Like']] = relationship(cascade='all, delete-orphan')

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
  likes: Mapped[list['Like']] = relationship()
  followings: Mapped[list['Follow']] = relationship(foreign_keys='Follow.follower_id')
  followers: Mapped[list['Follow']] = relationship(foreign_keys='Follow.following_id')

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


class Follow(Base):
  __tablename__ = 'follows'

  # 팔로잉 = 화살표 받는사람
  following_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)

  # 팔로워 = 화살표 보내는 사람
  follower_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
  