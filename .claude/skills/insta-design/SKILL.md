---
name: insta-design
description: insta의 templates 화면(HTML · CSS)을 꾸밀 때 쓴다. design/DESIGN.md의 디자인과 SCREENS.md의 화면 약속을 지키며 한 페이지씩 고친다.
---

# insta 화면 꾸미기

## 순서

1. `design/DESIGN.md`를 읽는다. 비어 있는 항목은 지어내지 않고, 고치기 전에 물어본다.
2. `SCREENS.md`에서 이 페이지의 주소 · 템플릿 · 받는 변수 · 폼 칸 `name` · `action`을 확인한다. 이 페이지가 `SCREENS.md`에 없으면 고치지 않고, 적어 달라고 한다.
3. 부탁받은 템플릿 하나와 `static/style.css`만 고친다.
   - 배경 · 다크 모드 · 위쪽 메뉴 · 글꼴처럼 모든 페이지에 걸리는 것은 `base.html` 몫이다. 처음에는 `base.html`부터 꾸민다.
   - 다른 페이지를 꾸밀 때 `base.html`에서 할 일이 보이면 고치지 않고 보고에 적는다.
4. `base.html`에 Bootstrap CDN 줄이 없으면 CSS 줄은 `<head>` 안 `/static/style.css` 줄 **위**에, JS 줄은 `</body>` 바로 위에 넣는다.

## 끝나면 보고

1. `DESIGN.md` 항목마다 — 어떤 클래스나 CSS로 반영했는지
2. 참고한 공식 문서 주소
3. `SCREENS.md` 약속 확인 표

| 약속 | 고치기 전 | 고친 뒤 | 같음 |
| --- | --- | --- | --- |
| 받는 변수 | `posts` | `posts` | O |
| 폼 `action` · `method` | … | … | O |
| 입력 칸 `name` | … | … | O |
| 링크 `href` | … | … | O |

4. 브라우저에서 확인할 곳 — 어느 페이지의 어느 부분을 보면 되는지