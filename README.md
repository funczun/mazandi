# 🌱 Mazandi-36주

본 프로젝트는 [원작](https://github.com/mazassumnida/mazandi)을 포크하여, **잔디 표시 기간을 기존 18주 → 36주로 수정한 버전**입니다.

## Install

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

## Usage

Solved.ac 잔디를 GitHub 프로필 `README.md`에 추가할 수 있습니다.  
아래 `{handle}` 부분에 **자신의 Solved.ac 아이디**를 입력하세요.

### Theme - Warm

```markdown
![Solved.ac Grass](https://mazandi-funczuns-projects.vercel.app/api?handle={handle})
```

### Theme - Cold

```markdown
![Solved.ac Grass (Cold)](https://mazandi-funczuns-projects.vercel.app/api?handle={handle}&theme=cold)
```

### Theme - Dark

```markdown
![Solved.ac Grass (Dark)](https://mazandi-funczuns-projects.vercel.app/api?handle={handle}&theme=dark)
```

## Additional Info

**원작 프로젝트:**  
[mazassumnida/mazandi](https://github.com/mazassumnida/mazandi)

**이 프로젝트의 배포 URL:**  
[https://mazandi-funczuns-projects.vercel.app](https://mazandi-funczuns-projects.vercel.app)
