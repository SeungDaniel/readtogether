# John Telegram Bot (Community Mode)

텔레그램 공동체 모드(단톡방 자동 본문 발송)용 파이썬 프로젝트입니다. 웹훅 없이 cron + long polling 구조로 동작하도록 설계되었습니다. 현재 저장소에는 **공동체 데일리 발송(daily_broadcast.py)** 이 구현되어 있습니다. 개인 1:1 모드는 추후 확장 예정입니다.

## 구성
- Python 3.x
- 주요 파일
  - `config.py` : 환경 변수 로더 및 그룹 설정 파서
  - `google_sheets_client.py` : 구글 시트 API 헬퍼
  - `plan_repository.py` : plan 시트 접근 (일차별 본문 조회)
  - `daily_broadcast.py` : 오늘의 본문 메시지 생성/전송
- 의존성: `requirements.txt`

## 구글 시트
- 스프레드시트 ID: `1jl1UJ6ZYT0oWzaiXAere0zhXgkebOtD829VQqW0zjyM`
- 시트 구조 (1행 헤더, 2행부터 데이터):
  - `plan` 시트: `day | ref | title | summary`
  - `progress` 시트: `user_id | username | current_day | last_read_at` (1:1 모드 확장용)
- 서비스 계정: `readtogether@readtogether-479613.iam.gserviceaccount.com`를 스프레드시트에 편집 권한으로 공유해야 합니다.

## 환경 변수 (.env 예시)
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_GROUP_CHAT_ID=-1003300234495
GOOGLE_SERVICE_ACCOUNT_FILE=/Users/namseunghyeon/PycharmProjects/PythonProject/John/readtogether-479613-373cc03b0945.json
SPREADSHEET_ID=1jl1UJ6ZYT0oWzaiXAere0zhXgkebOtD829VQqW0zjyM
PLAN_SHEET_NAME=plan
PROGRESS_SHEET_NAME=progress
START_DATE=2025-11-27
TIMEZONE=America/Phoenix
REQUEST_TIMEOUT_SECONDS=15
# 여러 그룹/플랜 사용 시:
# TELEGRAM_GROUP_CONFIG=[{"chat_id":"-1003300234495","plan_sheet":"plan","start_date":"2025-11-27"}]
```
- 단일 그룹이면 `TELEGRAM_GROUP_CHAT_ID(S)`로 충분합니다.
- 여러 그룹/플랜을 다르게 운용할 경우 `TELEGRAM_GROUP_CONFIG` JSON 배열을 사용합니다.

## 설치 및 실행 (로컬 확인)
```bash
pip install -r requirements.txt
source .env
# 드라이런으로 메시지 내용만 로그에 출력
DRY_RUN=true python daily_broadcast.py
# 실제 전송
python daily_broadcast.py
```

### 한 번에 실행(붙여넣기용)
```bash
cd /Users/namseunghyeon/PycharmProjects/PythonProject/John
pip install -r requirements.txt
set -a; source .env; set +a   # .env의 변수를 셸에 export
DRY_RUN=true python daily_broadcast.py
python daily_broadcast.py
```

## cron 예시 (우분투 서버)
서버 타임존 기준 오전 9시에 전송하려면:
```
0 9 * * * cd /path/to/project && /usr/bin/python3 daily_broadcast.py >> /path/to/logs/john_daily.log 2>&1
```
- 서버 타임존이 America/Phoenix와 다르면 `TIMEZONE` 또는 cron 시간대를 조정해야 합니다.
- `.env`와 서비스 계정 키(JSON)는 서버에 배포 후 적절한 경로로 설정하세요.

## 문제 해결
- 403 PERMISSION_DENIED: 스프레드시트에 서비스 계정을 편집 권한으로 공유했는지 확인.
- 전송 안 됨: `START_DATE`가 미래인지 확인, 혹은 `plan` 시트에 해당 `day` 행이 있는지 확인.
- 여러 그룹: `TELEGRAM_GROUP_CONFIG` JSON에 `chat_id`, `plan_sheet`, `start_date`를 넣으면 그룹별로 다른 플랜/시작일을 사용할 수 있습니다.

## 서버 배포를 위해 필요한 정보
로컬이 아닌 우분투 서버에 배포하려면 아래 정보를 알려주세요.
- 파이썬 실행 경로 (`which python3`)와 원하는 프로젝트 배포 경로
- 서버 타임존 (cron 기준) 또는 TIMEZONE을 무엇으로 둘지
- 로그 경로 선호 (`/var/log/...` 또는 프로젝트 내부 `logs/`)
- `.env`/서비스 계정 JSON을 저장할 경로 및 퍼미션 정책
- cron 등록 여부: 직접 등록할지, 등록 명령을 준비해드리면 되는지

## 다음 단계 (제안)
- 서버에 `.env`와 서비스 계정 JSON 배치 후 권한 확인
- 스프레드시트 공유 완료 확인
- (옵션) 여러 그룹/플랜이 필요하면 `TELEGRAM_GROUP_CONFIG` 정의
- 개인 1:1 폴링 봇(`bot_polling.py`) 구현 착수 가능
