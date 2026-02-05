# 프로젝트 구조 (Project Structure)

## 📂 폴더 구조

```
John/
├── src/                      # 소스 코드
│   ├── daily_broadcast.py    # 핵심: 매일 발송 스크립트
│   ├── callback_handler.py   # Webhook 서버 (읽음 인증 처리)
│   ├── book_registry.py      # 책 메타데이터 (john, isaiah 등)
│   ├── config.py             # 환경 변수 및 설정
│   ├── constants.py          # 상수 및 이모지
│   ├── google_sheets_client.py  # Google Sheets API 클라이언트
│   ├── group_repository.py   # 그룹 채팅방 관리
│   ├── plan_repository.py    # 읽기 플랜 데이터 관리
│   ├── log_repository.py     # 로그 저장
│   └── utils.py              # 유틸리티 함수
├── archive/                  # 보관된 레거시 코드
│   ├── bot_polling.py        # (제거됨) 1:1 폴링 봇
│   ├── keyboard_factory.py   # (제거됨) 키보드 생성
│   └── progress_repository.py # (제거됨) 개인 진도 관리
├── config/                   # 설정 파일
│   ├── .env                  # 환경 변수
│   └── credentials.json      # Google 서비스 계정 키
├── data/                     # 데이터 파일
│   └── isaiah_plan.csv       # 이사야 94일 플랜
├── docs/                     # 문서
└── requirements.txt          # Python 의존성
```

## 📄 핵심 파일 설명

### `src/daily_broadcast.py`
- 매일 Cron으로 실행되어 각 그룹에 오늘의 본문 발송
- `book_registry`에서 책 정보를 가져와 동적 메시지 생성
- `[✅ 읽었어요]` 인라인 버튼 포함

### `src/callback_handler.py`
- Flask 기반 Webhook 서버
- 사용자가 읽음 버튼 클릭 시 호출됨
- `confirmations` 시트에 읽음 기록 저장

### `src/book_registry.py`
- 지원 책 메타데이터 관리
- `john`: 요한복음 66일, `plan` 시트
- `isaiah`: 이사야 94일, `plan_isaiah` 시트

### `archive/` 폴더
- 리팩토링 과정에서 제거된 레거시 코드 보관
- 향후 참고용으로 유지
