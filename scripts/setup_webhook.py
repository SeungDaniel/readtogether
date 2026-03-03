#!/usr/bin/env python3
"""
setup_webhook.py
이 스크립트는 도메인이 없는 오라클 클라우드 서버(순수 IP)에서
텔레그램 웹훅을 작동시키기 위해 '자체 서명된 인증서(Self-Signed Certificate)'를
생성하고, 이를 텔레그램 서버에 업로드하여 웹훅을 등록합니다.
"""

import os
import sys
import argparse
import requests

def run_command(cmd):
    print(f"Executing: {cmd}")
    if os.system(cmd) != 0:
        print(f"명령어 실행 실패: {cmd}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="웹훅 SSL 인증서 생성 및 등록 스크립트")
    parser.add_argument("ip", help="서버의 공인 IP (예: 161.153.60.71)")
    parser.add_argument("token", help="텔레그램 봇 API 토큰")
    args = parser.parse_args()

    ip_address = args.ip
    bot_token = args.token

    print("=== 1단계: 자체 서명된 SSL 인증서(Self-Signed Certificate) 생성 ===")
    
    # 사설 인증서 생성을 위해 openssl 사용
    # IP 주소를 CN(Common Name)에 넣어야 텔레그램에서 이를 수락함
    openssl_cmd = (
        f"openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key "
        f"-x509 -days 3650 -out cert.pem -subj \"/C=KR/ST=Seoul/L=Seoul/O=JohnBot/CN={ip_address}\""
    )
    run_command(openssl_cmd)
    print("✅ cert.pem 과 private.key 파일이 생성되었습니다.\n")

    print("=== 2단계: 텔레그램 서버에 인증서와 함께 웹훅 URL 등록 ===")
    
    webhook_url = f"https://{ip_address}:8443/webhook"
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"

    try:
        with open('cert.pem', 'rb') as cert_file:
            print(f"웹훅 URL로 {webhook_url} 을 등록하며 cert.pem 파일을 전송합니다...")
            response = requests.post(
                api_url,
                data={'url': webhook_url},
                files={'certificate': cert_file}
            )
            response.raise_for_status()
            result = response.json()
            if result.get('ok'):
                print("✅ 성공: 텔레그램에 웹훅과 인증서가 정상적으로 등록되었습니다!\n")
            else:
                print(f"❌ 실패: {result}\n")
                sys.exit(1)
    except Exception as e:
        print(f"요청 중 에러가 발생했습니다: {e}")
        sys.exit(1)

    print("=== 모든 과정이 끝났습니다! ===")
    print("이제 기존에 켜져있는 gunicorn 서버를 끄고, 아래의 '보안(HTTPS)' 명령어로 다시 켜주세요:\n")
    print(f"  pkill -f gunicorn")
    print(f"  nohup gunicorn --pythonpath src -w 2 --certfile cert.pem --keyfile private.key -b 0.0.0.0:8443 callback_handler:app > nohup.out 2>&1 & ")
    print("\n※ 위 명령어로 서버를 켠 후에도 버튼 클릭이 무한 로딩이라면 오라클 클라우드의 방화벽에서 8443 포트가 막힌 것입니다!")

if __name__ == "__main__":
    main()
