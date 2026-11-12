---
paths:
  - "templates/**"
  - "static/**"
---

# 화면 파일 규칙

1. 있는 `{% %}` · `{{ }}`는 지우거나 고치지 않는다. 새로 쓸 때는 `SCREENS.md`에 적힌 변수 · 필터만 쓴다.
2. `a`의 `href` · `form`의 `action` · `method` · 입력 칸의 `name`은 바꾸지 않는다.
3. 새 링크는 `SCREENS.md`에 있는 주소만 쓴다.
4. Bootstrap 5.3 CDN(CSS · JS 두 줄)만 쓴다. 다른 라이브러리는 쓰지 않는다.
5. Bootstrap 클래스 이름과 CDN 줄은 기억으로 쓰지 않는다. context7로 Bootstrap 5.3 공식 문서(`/websites/getbootstrap/5.3`)를 찾아본 뒤 문서에 있는 그대로 쓴다. 찾은 결과에 없는 클래스는 한 번 더 찾아본다.
6. Bootstrap 클래스로 못 하는 것은 `static/style.css`에만 쓴다. `style=""` 속성과 `<style>` 태그는 쓰지 않는다. `--bs-`로 시작하는 변수는 바꾸지 않는다.
7. 입력 칸에는 `required`를 넣고, 게시물 내용 칸은 `textarea`로 한다. `textarea`의 원래 내용은 태그 사이에 붙여 쓴다.
8. 부탁받은 템플릿 하나와 `static/style.css`만 고친다.