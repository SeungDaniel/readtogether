# John Bot - 통합 서버 매뉴얼 (Server Manual)

이 문서는 John Bot 서버의 **설정(Setup), 테스트(Test), 배포(Deploy), 운영(Operation)** 및 **터미널 명령어(Cheatsheet)**를 하나로 통합한 가이드입니다.

---

## 1. 현재 상태 3분 진단 (Quick Check)
서버에 들어가자마자 "지금 봇이 살아있나?" 확인하는 방법입니다.

```bash
# 1단계: 실행 중인 봇 확인 (경비원)
ps aux | grep python
# ✅ 출력에 "python3 src/bot_polling.py"가 보이면 작동 중!

# 2단계: 예약된 알림 작업 확인 (배달원)
crontab -l
# ✅ 출력에 "0 * * * * ... src/daily_broadcast.py"가 보이면 정상!

# 3단계: 파일 확인
ls -l
# ✅ "john-bot" 폴더나 프로젝트 파일들이 보여야 함
```

---

## 2. 서버 초기 설정 (First Process)
서버를 처음 받았거나 포맷했을 때 한 번만 수행합니다.

### A. 필수 패키지 설치
```bash
# 파이썬3 및 pip 설치
sudo apt update
sudo apt install python-is-python3 python3-pip -y
```

### B. 라이브러리 설치
```bash
cd ~/john-bot
pip install -r requirements.txt
```

---

## 3. 배포 가이드 (Deployment)
로컬에서 개발한 코드를 서버에 반영할 때 사용합니다.

### A. 최신 코드 받기
```bash
cd ~/john-bot
git pull origin main
```
*에러 발생 시*: `git stash`로 로컬 변경사항을 치운 뒤 다시 `git pull` 해보세요.

### B. 중요 파일 업데이트 (필요 시)
`config/.env`나 `google-key.json`이 바뀌었다면 서버에서도 수정해줘야 합니다.
```bash
nano config/.env
# 붙여넣기 후 저장: Ctrl+O -> Enter -> Ctrl+X
```

### C. 봇 재시작 (Restart)
코드가 바뀌면 봇을 껐다 켜야 반영됩니다.
```bash
# 1. 기존 봇 종료
pkill -f bot_polling.py

# 2. 봇 백그라운드 실행
nohup python3 src/bot_polling.py > nohup.out 2>&1 &

# 3. 잘 켜졌는지 로그 확인
tail -f nohup.out
# (나가려면 Ctrl+C)
```

---

## 4. 문제 해결 (Troubleshooting)

### Q. 봇이 응답을 안 해요!
1. `ps aux | grep python`으로 프로세스가 살아있는지 확인하세요.
2. 없다면 `nohup ...` 명령어로 다시 켜세요.
3. 있다면 `tail -f nohup.out`으로 에러 로그가 계속 뜨는지 보세요.

### Q. 아침 알림이 안 와요! (Daily Broadcast)
1. `crontab -l`로 스케줄이 등록되어 있는지 보세요.
2. 시간 확인: `date` 명령어로 서버 시간이 한국 시간과 달라도, 봇 로그에는 `LocalTime`이 정상적으로 찍히는지 확인하세요.
   * 확인법: `python3 src/daily_broadcast.py` (수동 실행)
   * 강제 발송 테스트: `FORCE_SEND=true python3 src/daily_broadcast.py`

---

## 5. 터미널 명령어 치트시트 (Cheatsheet)

### 필수 단축키
- **명령어 취소**: `Ctrl + C` (실행 중인 거 멈출 때)
- **화면 지우기**: `Ctrl + L`
- **로그에서 검색**: `/검색어` (less나 vi에서)
- **편집기 저장/종료(Nano)**: `Ctrl+O` (저장), `Ctrl+X` (종료)

### 파일/폴더 관리
- `ls -al`: 파일 목록 자세히 보기
- `cd [폴더명]`: 이동 (`cd ..` 상위로, `cd ~` 홈으로)
- `cp [원본] [복사본]`: 파일 복사
- `mv [원본] [이동경로]`: 파일 이동/이름변경
- `rm [파일]`: 삭제 (주의! 되살릴 수 없음)

### 프로세스 관리
- `ps aux`: 실행 중인 모든 프로그램 보기
- `kill [PID]`: 특정 프로세스 죽이기 (PID는 ps에서 확인한 숫자)
- `pkill -f [이름]`: 이름으로 프로세스 죽이기 (예: `pkill -f python`)

---
**Tip**: 이 파일(`docs/SERVER_GUIDE.md`)은 서버의 `john-bot/docs` 폴더에도 있으니, 언제든 `cat docs/SERVER_GUIDE.md`로 열어보실 수 있습니다!
