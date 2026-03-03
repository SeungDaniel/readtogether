# John Bot - 통합 서버 매뉴얼 (Server Manual)

이 문서는 John Bot 서버의 **설정, 배포, 운영** 및 **터미널 명령어(Cheatsheet)**를 하나로 통합한 가이드입니다. 
(※ V2 버전: Webhook + Daily Broadcast 아키텍처 기준)

---

## 1. 현재 상태 3분 진단 (Quick Check)
서버에 들어가자마자 "지금 봇이 살아있나?" 확인하는 방법입니다.

```bash
# 1단계: 실행 중인 Webhook 서버 확인
ps aux | grep gunicorn
# ✅ 출력에 "gunicorn ... src.callback_handler:app"이 보이면 켜져있음!

# 2단계: 예약된 아침 발송 작업 확인 (Cron)
crontab -l
# ✅ 출력에 "0 8 * * * ... src/daily_broadcast.py"가 보이면 정상등록됨!

# 3단계: 프로젝트 폴더 확인
cd ~/john-bot && ls -l
```

---

## 2. 서버 설정 (초기 세팅)

### A. 필수 패키지 설치
```bash
sudo apt update
sudo apt install python-is-python3 python3-pip -y
```

### B. 라이브러리 설치
```bash
cd ~/john-bot
pip install -r requirements.txt
# flask, gunicorn 등이 설치됩니다.
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

### B. 봇 재시작 (Restart)
코드가 바뀌면 백그라운드 서버를 껐다 켜야 반영됩니다.

```bash
# 1. 기존 서버 종료
pkill -f gunicorn

# 2. 백그라운드 재실행 (포트 8443)
nohup gunicorn --pythonpath src -w 2 -b 0.0.0.0:8443 callback_handler:app > nohup.out 2>&1 &

# 3. 잘 켜졌는지 에러 로그 확인
tail -f nohup.out
```

---

## 4. 텔레그램 웹훅(Webhook) 등록
텔레그램 서버가 우리 서버의 주소를 알 수 있도록 웹훅을 등록해야 **[✅ 읽었어요]** 버튼이 작동합니다.

* `https://api.telegram.org/bot<토큰>/setWebhook?url=https://<서버도메인>:8443/webhook` 주소로 브라우저에 접속하거나 아래 Curl을 실행하세요.

```bash
curl -X POST "https://api.telegram.org/bot<여기에_봇토큰>/setWebhook?url=https://<여기에_서버아이피_또는_도메인>:8443/webhook"
```

---

## 5. 문제 해결 (Troubleshooting)

### Q. [읽었어요] 버튼을 눌렀는데 '알 수 없는 오류'가 나거나 모래시계만 돌아요!
1. `ps aux | grep gunicorn`으로 웹훅 서버가 살아있는지 확인하세요.
2. 꺼져있다면 3.B 항목의 `nohup` 명령어로 켜세요.
3. 켜져있다면, **4번 웹훅 등록** 항목을 다시 실행해서 텔레그램에 올바른 서버 IP가 등록되어 있는지 확인하세요.
4. 오라클 클라우드의 백단 방화벽 (포트 8443) 개방 여부, 또는 Nginx 리버스 프록시 세팅을 점검해야 합니다.

### Q. 아침 단톡방 알림이 안 와요! 
1. `crontab -l`로 스케줄 시간(`0 8 * * * ` 등)이 제대로 등록되어 있는지 보세요.
2. 수동 발송 테스트 `FORCE_SEND=true python3 src/daily_broadcast.py`를 실행해 에러(예: 구글 시트 오류)가 뜨는지 확인하세요.

---

## 6. 터미널 명령어 치트시트 (Cheatsheet)

- **종료/취소**: `Ctrl + C`
- **화면 지우기**: `Ctrl + L`
- **파일목록**: `ls -al`
- **백그라운드 로그 보기**: `tail -f nohup.out`
- **프로세스 끄기**: `pkill -f [이름]`
