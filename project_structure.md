# 프로젝트 구조 (Project Structure)

이 문서는 프로젝트의 폴더 구조와 각 파일의 역할을 설명합니다.

## 📂 폴더 구조

```
John/
├── config/                 # 설정 및 인증 관련 파일
│   ├── .env               # 환경 변수 설정 파일 (토큰, 시트 ID 등)
│   └── readtogether-*.json # 구글 서비스 계정 인증 키 (JSON)
├── docs/                   # 프로젝트 문서
│   ├── Plan.md            # 프로젝트 기획 및 로드맵
│   ├── V1개발지시서.md      # V1 개발 상세 명세서
│   └── USER_GUIDE.md      # 사용자 가이드
├── src/                    # 소스 코드
│   ├── bot_polling.py     # 텔레그램 봇 메인 실행 파일 (1:1 채팅 폴링)
│   ├── daily_broadcast.py # 공동체 단톡방 데일리 발송 스크립트 (Cron 실행용)
│   ├── config.py          # 환경 변수 로드 및 설정 관리
│   ├── google_sheets_client.py # 구글 시트 API 연동 클라이언트
│   ├── group_repository.py     # 그룹 채팅방 데이터 관리
│   ├── log_repository.py       # 로그 데이터 관리
│   ├── plan_repository.py      # 읽기 플랜(본문) 데이터 관리
│   └── progress_repository.py  # 사용자별 진도 데이터 관리
├── README.md               # 프로젝트 메인 설명 파일
└── requirements.txt        # 파이썬 의존성 패키지 목록
```

## 📄 파일 및 폴더 상세 설명

### 1. `src/` (Source Code)
프로젝트의 핵심 소스 코드가 위치한 폴더입니다.

- **`bot_polling.py`**:
  - 텔레그램 봇의 메인 스크립트입니다.
  - `getUpdates` 방식을 사용하여 사용자의 메시지를 폴링하고, 1:1 채팅 명령(`/start_john`, `/next` 등)을 처리합니다.
  - 오라클 클라우드 등 서버에서 상시 실행되어야 합니다.

- **`daily_broadcast.py`**:
  - 매일 정해진 시간에 공동체 단톡방으로 '오늘의 본문'을 발송하는 스크립트입니다.
  - 서버의 `cron` 등을 통해 스케줄링하여 실행합니다.

- **`config.py`**:
  - 환경 변수(`os.environ`)를 로드하고, 프로젝트 전반에서 사용하는 설정값(토큰, 시트 이름 등)을 제공합니다.

- **`google_sheets_client.py`**:
  - Google Sheets API와 통신하는 저수준 클라이언트입니다.
  - 인증 처리 및 시트 읽기/쓰기 기능을 담당합니다.

- **`*_repository.py`**:
  - 각 데이터 도메인별로 구글 시트와 상호작용하는 로직을 캡슐화한 파일들입니다.
  - `plan_repository.py`: 요한복음 읽기 플랜 조회
  - `progress_repository.py`: 사용자별 진도 조회 및 업데이트
  - `group_repository.py`: 등록된 그룹 채팅방 관리
  - `log_repository.py`: 활동 로그 저장

### 2. `config/` (Configuration)
설정 파일과 보안 관련 파일이 위치합니다.

- **`.env`**: API 키, 봇 토큰 등 민감한 정보를 담고 있는 환경 변수 파일입니다.
- **`readtogether-*.json`**: 구글 클라우드 플랫폼(GCP) 서비스 계정 인증 키 파일입니다.

### 3. `docs/` (Documentation)
프로젝트 이해를 돕는 문서들입니다.

- **`V1개발지시서.md`**: 개발 목표, 아키텍처, 기능 요구사항이 상세히 기술된 명세서입니다.
- **`Plan.md`**: 프로젝트의 전체적인 방향성과 단계별 로드맵이 담겨 있습니다.
- **`USER_GUIDE.md`**: 실제 봇 사용자를 위한 안내서입니다.
