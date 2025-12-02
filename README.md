# 요한복음 데일리 텔레그램 봇 (John Daily Telegram Bot)

요한복음 읽기 로드맵을 기반으로 공동체와 개인이 함께 말씀을 읽을 수 있도록 돕는 텔레그램 봇 프로젝트입니다.

## 🎯 프로젝트 목표

1.  **공동체 모드 (단톡방)**: 매일 정해진 시간에 '오늘의 본문'을 자동으로 발송합니다.
2.  **개인 모드 (1:1 채팅)**: 사용자가 자신의 속도에 맞춰 `/next` 명령어로 퀘스트처럼 진도를 나갈 수 있습니다.

## 📂 프로젝트 구조

자세한 구조는 [project_structure.md](project_structure.md)를 참고하세요.

- `src/`: 봇 소스 코드
- `config/`: 설정 파일 (.env, 구글 인증 키)
- `docs/`: 기획 및 개발 문서

## 🚀 설치 및 실행 방법

### 1. 환경 설정

1.  **Python 3.9+** 설치가 필요합니다.
2.  의존성 패키지를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

### 2. 설정 파일 준비

`config/` 폴더 내에 필요한 설정 파일이 있는지 확인하세요.

- **`config/.env`**: 텔레그램 봇 토큰, 구글 시트 ID 등 환경 변수 설정
- **`config/readtogether-*.json`**: 구글 서비스 계정 인증 키

### 3. 실행 방법

프로젝트 루트 디렉토리에서 아래 명령어로 실행합니다.

#### 🤖 1:1 봇 실행 (Polling)
개인 퀘스트 모드를 처리하는 봇을 실행합니다. (상시 실행 필요)

```bash
# 환경변수 로드 후 실행 (예시)
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/bot_polling.py
```
*참고: `.env` 파일의 내용을 환경 변수로 로드한 후 실행해야 합니다.*

#### 📢 데일리 발송 실행 (Broadcast)
공동체 단톡방에 오늘 본문을 발송합니다. (Cron 등으로 매일 1회 실행)

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/daily_broadcast.py
```

## 🛠 기술 스택

- **Language**: Python 3
- **Platform**: Telegram Bot API
- **Database**: Google Sheets (Plan & Progress)
- **Infrastructure**: Oracle Cloud (Ubuntu)

## 📚 문서

- [개발 지시서 (V1)](docs/V1개발지시서.md)
- [기획안 (Plan)](docs/Plan.md)
- [사용자 가이드](docs/USER_GUIDE.md)
