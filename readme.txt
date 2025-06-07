Strength Diary - 장점 발견 일기 웹사이트
==========================================

이 프로젝트는 사용자가 작성한 일기에서 장점을 자동 분석하여 보여주는 웹 애플리케이션입니다.  
Flask 웹 프레임워크와 transformers 모델을 사용하며 SQLite를 기본 DB로 사용합니다.

---

실행 방법 (Windows 기준, Python 설치 필요)
-------------------------------------------

1. [Python 3.8+ 설치](https://www.python.org/downloads/) (이미 되어 있다면 생략)

2. 프로젝트 디렉토리로 이동

3. 가상환경 생성 (권장)
   > python -m venv venv

4. 가상환경 실행
   > venv\Scripts\activate

5. 필요한 라이브러리 설치
   > pip install -r requirements.txt

   ※ requirements.txt가 없을 경우:
   > pip install flask sqlalchemy transformers torch

6. 데이터베이스 초기화 (최초 1회만 수행)
   > flask --app main db init  
   > flask --app main db migrate  
   > flask --app main db upgrade

7. 서버 실행
   > python main.py

8. 웹브라우저에서 접속
   > 주소창에 http://127.0.0.1:5000 입력

---

주요 디렉토리 구성
---------------------
- main.py: Flask 메인 실행 파일
- backend/: 백엔드 로직 및 모델 관리
- templates/: HTML 템플릿
- static/: JS, CSS 등 정적 자원
- migrations/: DB 마이그레이션
- venv/: (가상환경)

---

관리자 계정 (직접 등록 방식)
-------------------------------
- 회원가입 시, 아이디를 admin으로 입력하면 관리자 권한이 부여됩니다.
- 예시:
   ID: admin
   PW: 원하는 비밀번호
   닉네임: 자유 입력

※ 최초 관리자 계정은 스스로 등록해야 하며 따로 자동 생성되진 않습니다.

---

Trouble Shooting
-------------------
실행 중 ModuleNotFoundError 발생 시:
> 필요한 패키지를 `pip install`로 설치하세요.

웹에서 접속 안 될 경우:
> 방화벽 또는 백그라운드 실행 여부 확인 후 다시 python main.py