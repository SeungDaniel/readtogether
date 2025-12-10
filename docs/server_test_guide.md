# 서버 테스트 가이드 (Python3 사용)

서버에서 봇이 잘 돌아가는지 확인하는 단계별 가이드입니다.
`python` 명령어 대신 확실한 **`python3`** 명령어를 사용합니다.

## 0단계: 무엇이 돌고 있는지 확인 (현재 상태)
지금 서버에서 어떤 봇이나 프로그램이 실행 중인지 궁금하다면?

```bash
# 1. 실행 중인 파이썬 프로그램 확인
# "python3 src/bot_polling.py" 같은 게 보이면 실행 중인 겁니다.
ps aux | grep python

# 2. 현재 폴더(john-bot)에 무슨 파일이 있는지 확인
ls -l
```

## 1단계: 직접 실행해서 에러 확인하기
백그라운드로 돌리기 전에, 눈으로 직접 실행해서 에러가 없는지 봅니다.

```bash
# 1. 프로젝트 폴더로 이동
cd ~/john-bot

# 2. 환경변수 설정 (필수!)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 3. 봇 실행 (직접 보기)
python3 src/bot_polling.py
```

*   **성공 시**: `[INFO] Bot info loaded...` 같은 로그가 뜨고 멈춰있으면 정상입니다.
    *   테스트가 끝났으면 `Ctrl + C`를 눌러서 끄세요.
*   **실패 시**: 에러 메시지가 화면에 나옵니다. (예: `ModuleNotFoundError` 등)

## 2단계: 24시간 무중단 실행 (nohup)
테스트가 성공했다면, 이제 터미널을 꺼도 돌아가게 만듭니다.

```bash
# 1. 백그라운드 실행 (python3 사용)
nohup python3 src/bot_polling.py > nohup.out 2>&1 &

# 2. 잘 켜졌는지 확인
ps aux | grep python
```
*   `python3 src/bot_polling.py` 줄이 보이면 성공입니다!

## 3단계: 로그 확인하기
봇이 잘 작동하고 있는지 로그 파일로 확인합니다.

```bash
# 실시간 로그 보기
tail -f nohup.out
```
*   그만 보려면 `Ctrl + C` (봇은 안 꺼짐)

## 4단계: 봇 끄기 (종료)
봇을 완전히 끄고 싶을 때 사용합니다.

```bash
pkill -f bot_polling.py
```
