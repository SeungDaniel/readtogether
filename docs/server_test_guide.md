# 서버 테스트 및 배포 가이드 (Webhook 버전)

봇이 "폴링(Polling)" 방식에서 "웹훅(Webhook)" 방식으로 업그레이드되었습니다. 
이제 봇은 상시로 텔레그램을 확인하는 대신, **버튼이 눌렸을 때만 웹 서버(Flask)가 요청을 받아 처리**합니다.

## 0단계: 무엇이 돌고 있는지 확인 (현재 상태)

지금 서버에서 어떤 봇이나 프로그램이 실행 중인지 확인합니다.

```bash
# 1. 실행 중인 파이썬 웹 서버(gunicorn 또는 python3) 확인
ps aux | grep gunicorn
# 또는
ps aux | grep python

# 2. 현재 폴더(john-bot)에 무슨 파일이 있는지 확인
ls -l
```

## 1단계: 직접 실행해서 에러 확인하기

백그라운드로 돌리기 전에, 먼저 눈으로 직접 실행해서 에러가 없는지 봅니다.

```bash
# 1. 프로젝트 폴더로 이동
cd ~/john-bot

# 2. 환경변수 설정 (필수!)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 3. Webhook 서버 실행 (gunicorn 사용 권장)
gunicorn -w 2 -b 0.0.0.0:8443 src.callback_handler:app
```

* **성공 시**: `[INFO] Starting gunicorn...` 같은 로그가 뜨고 대기 상태에 들어갑니다.
  * 테스트가 끝났으면 `Ctrl + C`를 눌러서 끄세요.
* **실패 시**: 에러 메시지가 화면에 나옵니다. (`Address already in use`면 이미 실행 중인 것입니다.)

## 2단계: 24시간 무중단 실행 (nohup 또는 systemctl)

간단한 방법인 `nohup`을 사용하여 화면을 꺼도 서버가 계속 돌아가게 만듭니다.

```bash
# 1. 백그라운드 실행 (gunicorn 사용)
nohup gunicorn -w 2 -b 0.0.0.0:8443 src.callback_handler:app > nohup.out 2>&1 &

# 2. 잘 켜졌는지 확인
ps aux | grep gunicorn
```

## 3단계: 텔레그램에 Webhook 주소 알려주기 (매우 중요!)

봇 서버를 켰으면, 텔레그램 본사에 "버튼이 눌리면 이 주소로 알려줘!" 라고 등록해야 합니다. **최초 1회만** 하면 됩니다.

아래 명령어의 `<봇토큰>`과 `<서버IP또는도메인>`을 실제 값으로 바꿔서 실행하세요.
(서버 터미널이나 내 컴퓨터 아무 데서나 한 번만 실행하면 됩니다.)

```bash
curl -X POST "https://api.telegram.org/bot<봇토큰>/setWebhook?url=https://<서버IP또는도메인>:8443/webhook"
```

* **주의:** 텔레그램 웹훅은 기본적으로 **HTTPS** (보안 연결)를 요구합니다. 가장 좋은 방법은 Nginx나 Cloudflare 등을 통해 도메인에 SSL(https)을 씌우는 것입니다.

* **결과 확인**:
  ```json
  {"ok":true,"result":true,"description":"Webhook was set"}
  ```
  이런 응답이 오면 성공입니다!

## 4단계: 로그 확인하기

봇이 버튼 클릭을 잘 처리하고 있는지 확인합니다.

```bash
# 실시간 로그 보기
tail -f nohup.out
```

## 5단계: 서버 끄기 (종료)

서버를 완전히 끄거나 재시작하고 싶을 때 사용합니다.

```bash
pkill -f gunicorn
```
