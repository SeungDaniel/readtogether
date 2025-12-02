# 🧪 요한복음 봇 테스트 가이드 (Test Guide)

이 문서는 봇을 개발하거나 배포하기 전에 다양한 기능을 테스트하고 디버깅하는 방법을 안내합니다.

## 🚀 빠른 실행 명령어 모음 (복사 붙여넣기용)

아래 명령어들을 순서대로 터미널에 복사해서 실행하세요.

### 1. 환경 설정 및 패키지 설치
```bash
cd /Users/namseunghyeon/PycharmProjects/PythonProject/John
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### 2. 봇 실행 (1:1 채팅 & 답장 리액션)
*이 명령어를 실행하면 봇이 켜집니다. 끄려면 `Ctrl+C`를 누르세요.*
```bash
python src/bot_polling.py
```

### 3. 데일리 발송 테스트 (새 터미널 탭에서 실행)
*주의: 실제 단톡방에 메시지가 전송됩니다. 테스트 전 `config/.env`에서 타겟 채팅방 ID를 확인하세요.*
```bash
cd /Users/namseunghyeon/PycharmProjects/PythonProject/John
export PYTHONPATH=$PYTHONPATH:$(pwd)
python src/daily_broadcast.py
```

---

## 📂 상세 테스트 가이드

### 1. 준비 단계
먼저 `config/.env` 파일을 확인하여 필요한 환경변수(`TELEGRAM_BOT_TOKEN` 등)가 설정되어 있는지 확인합니다.
*   **참고**: 테스트를 위해 실제 단톡방 ID는 주석 처리되어 있을 수 있습니다. 발송 테스트 시 주석을 해제하거나 테스트용 방 ID를 입력하세요.

### 2. 개인 모드 테스트 (1:1)
`src/bot_polling.py`를 실행한 상태에서 텔레그램 봇에게 말을 걸어봅니다.
1.  `/start_john` 입력 → 환영 메시지와 버튼 확인
2.  `[🚀 1일차 시작하기]` 버튼 클릭 → 다음 본문 수신 확인
3.  `/status` 입력 → 현재 진도 확인

### 3. 공동체 모드 테스트 (데일리 발송)
`src/daily_broadcast.py`는 크론(Cron) 스케줄러에 의해 실행되도록 설계된 스크립트입니다.
*   **Dry Run (전송 없이 로그만 확인)**:
    ```bash
    DRY_RUN=true python src/daily_broadcast.py
    ```
*   **실제 전송**:
    ```bash
    python src/daily_broadcast.py
    ```

### 4. 답장 리액션 테스트
단톡방에서 봇이 보낸 메시지(또는 봇의 아무 메시지)에 **답장(Reply)**을 보내보세요.
*   봇이 👍(따봉) 이모지를 달아주면 성공입니다.
*   반응이 없다면 봇이 해당 그룹의 메시지를 볼 권한(Privacy Mode Off)이 있는지 확인하세요.
