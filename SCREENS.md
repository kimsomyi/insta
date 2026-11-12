# 화면 약속

`.py`(직접 치는 코드)와 `templates/`(Claude와 꾸미는 화면)가 만나는 자리.
아래 이름은 바꾸지 않는다. 페이지를 꾸미기 전에 그 페이지 칸을 먼저 적는다.

## 모든 화면이 받는 변수

- `user` — 지금 로그인한 사용자. 로그인 안 했으면 `None`
- 로그인했는지는 `{% if user %}`로 나눈다

## 게시물 칸 (`post`)

| 칸 | 타입 | 화면에서 |
| --- | --- | --- |
| `id` | int | 주소(`/posts/{{ post.id }}`) |
| `content` | str | 본문 |
| `image_url` | str 또는 `None` | 사진 `<img src="{{ post.image_url }}">`. 사진 없는 옛 글이 있어서 `{% if post.image_url %}` 안에 둔다 |
| `created_at` | datetime | `{{ post.created_at.strftime('%Y-%m-%d %H:%M') }}` |
| `user` | 사용자 | 글쓴이 이름 `{{ post.user.username }}` · 프로필 링크 `/users/{{ post.user.username }}` |
| `user_id` | int | 내 글인지 확인(`user.id == post.user_id`) |
| `comments` | 댓글 목록 | 댓글 수(`length` 필터) · 상세의 댓글 목록 |
| `likes` | 좋아요 목록 | 좋아요 수(`length` 필터) |

## 페이지

### 공통 틀

- 템플릿: `base.html` — 다른 템플릿이 `{% extends 'base.html' %}`로 쓴다
- 블록: `title` · `content`
- 메뉴 — 로그인했을 때: `/posts` · `/posts/new` · 내 프로필 `/users/{{ user.username }}` · 이름 · 로그아웃 폼(`method="post"` `action="/logout"`, 칸 없음)
- 메뉴 — 로그인 안 했을 때: `/posts` · `/signup` · `/login`
- CSS: `/static/style.css`(Bootstrap CSS 줄 아래)

### 전체 글

- 주소: `GET /posts`
- 템플릿: `list.html`
- 받는 변수: `posts` — 게시물 목록(새 글이 위) · `liked_ids` — 내가 좋아요한 게시물 번호 목록(로그인 안 했으면 빈 목록)
- 글마다: 사진 · 본문 · 글쓴이(프로필 링크) · 댓글 수 · 좋아요 수 · 올린 시각 · 상세 링크
- 좋아요 폼(글마다): `method="post"` `action="/posts/{{ post.id }}/likes"` — 칸 없음. 버튼 글자는 `{% if post.id in liked_ids %}`로 나눈다
- 링크: 게시물마다 `/posts/{{ post.id }}`