# Future Roadmap & Improvements
# 향후 발전 계획

This document outlines potential directions for evolving the John Daily Bot project, focusing on UX, Engineering, and Analytics.
이 문서는 요한복음 데일리 봇 프로젝트의 향후 발전 방향(UX, 엔지니어링, 데이터 분석)을 정리합니다.

## 1. User Experience (UX) Expansion: "More Fun & Smart"
## 1. 사용자 경험 (UX) 확장: "더 재미있고 똑똑하게"

*   **Gamification (게이미피케이션)**:
    *   **Streak Badges**: "3-Day Streak! 🔥", "7-Day Streak! 🏆" notifications to motivate users.
    *   **연속 읽기 배지**: "3일 연속 달성! 🔥", "7일 연속! 🏆" 같은 알림으로 동기 부여.
    *   **Level System**: Ranks based on read count (e.g., Beginner -> Disciple -> Apostle).
    *   **레벨 시스템**: 읽은 날짜 수에 따라 등급 부여 (예: 초심자 -> 제자 -> 사도).

*   **AI Meditation Assistant (AI 묵상 도우미 - RAG)**:
    *   Users can ask questions like "Where is Bethany in today's text?", and the bot answers using learned data (commentaries, maps).
    *   사용자가 "오늘 본문에서 '베다니'가 어디야?"라고 물으면, 봇이 학습된 데이터(주석, 지도 정보)를 바탕으로 답변해주는 기능.

*   **Personalized Reminders (개인화 리마인더)**:
    *   Nudge users who haven't read yet at 9 PM: "Don't miss today's word!"
    *   아직 읽지 않은 사람에게만 저녁 9시에 "오늘 말씀 놓치지 않으셨나요?"라고 살짝 찔러주는 기능.

## 2. Technical Engineering: "Faster & More Stable"
## 2. 기술적 고도화: "더 빠르고 안정적으로"

*   **Webhook Transition (웹훅 전환)**:
    *   Switch from Polling (asking "Any msg?") to Webhook (Telegram notifies server).
    *   Reduces latency and server resource usage. Essential for production deployment.
    *   폴링(Polling) 방식에서 웹훅(Webhook) 방식으로 전환하여 반응 속도를 높이고 서버 자원을 절약.

*   **Database Integration (데이터베이스 도입)**:
    *   Use **SQLite** or **PostgreSQL** for main data storage.
    *   Use Google Sheets only as an Admin CMS (one-way sync) to prevent API throttling and improve performance.
    *   실제 데이터는 DB에 저장하고, 구글 시트는 관리자용 입력 도구로만 사용하여 성능과 안정성 확보.

*   **Docker Containerization (도커 컨테이너화)**:
    *   Package the environment so it runs with `docker-compose up` on any server (AWS, Oracle Cloud, etc.).
    *   어떤 서버에서도 즉시 실행 가능하도록 환경 패키징.

## 3. Data Analytics: "Spiritual Weather Map"
## 3. 데이터 분석: "공동체 영적 기상도"

*   **Dashboard Webpage (대시보드 웹페이지)**:
    *   Simple web view showing "Community Progress Rate", "Most Active Times", "Popular Verses".
    *   "이번 주 우리 공동체 진도율", "가장 많이 읽는 요일/시간대" 등을 보여주는 그래프 페이지.

*   **Automated Reports (자동 리포트)**:
    *   Weekly PDF/Image reports sent to leaders every Monday morning.
    *   매주 월요일 아침, 리더들에게 "지난주 리포트" 자동 발송.
