# 성경 함께 읽기 텔레그램 봇 (Bible Together Bot)

📖 공동체가 함께 성경을 읽을 수 있도록 돕는 텔레그램 봇입니다.

## 🎯 핵심 기능

### 1. 데일리 브로드캐스트
- 매일 정해진 시간에 **오늘의 본문**을 자동 발송
- 성구, 제목, 참고자료 링크 포함
- **[✅ 읽었어요]** 버튼으로 읽음 인증

### 2. Multi-Book 지원
| 책 | 총 일수 | 시트명 |
|----|--------|--------|
| 요한복음 | 66일 | `plan` |
| 이사야 | 94일 | `plan_isaiah` |

## 📂 프로젝트 구조

```
John/
├── src/
│   ├── daily_broadcast.py   # 핵심: 매일 발송 + 읽음 버튼
│   ├── callback_handler.py  # Webhook 서버 (버튼 클릭 처리)
│   ├── book_registry.py     # 책 메타데이터
│   ├── google_sheets_client.py
│   ├── group_repository.py
│   ├── plan_repository.py
│   └── config.py
├── archive/                  # 보관된 레거시 코드
├── config/
│   ├── .env
│   └── credentials.json
├── data/
│   └── isaiah_plan.csv       # 이사야 94일 플랜
└── docs/                     # 문서
```

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
`config/.env` 파일에 다음 설정:
```
TELEGRAM_BOT_TOKEN=your_token
SPREADSHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=config/credentials.json
```

### 3. 실행

#### 데일리 발송 (Cron)
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/daily_broadcast.py
```

#### Webhook 서버 (상시 실행)
```bash
gunicorn -w 2 -b 0.0.0.0:8443 src.callback_handler:app
```

## 📊 Google Sheets 구조

### groups 시트
| chat_id | plan_sheet | start_date | timezone | notification_time |
|---------|------------|------------|----------|-------------------|

### plan / plan_isaiah 시트
| Day | Ref | Title | Verse_Text | Verse_Ref | Image_URL | Youtube_Link |

### confirmations 시트 (읽음 인증)
| timestamp | user_id | username | chat_id | book_id | day |

## 🛠 기술 스택

- **Language**: Python 3.9+
- **Platform**: Telegram Bot API
- **Database**: Google Sheets
- **Webhook**: Flask + Gunicorn
- **Infra**: Oracle Cloud

## 📚 문서

- [향후 계획 (Roadmap)](docs/ROADMAP.md)
- [서버 가이드](docs/SERVER_GUIDE.md)
- [사용자 가이드](docs/USER_GUIDE.md)
