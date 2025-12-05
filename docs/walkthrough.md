# Bot UX and Performance Enhancements Walkthrough
# 봇 UX 및 성능 개선 워크스루

This document summarizes the changes made to the John Daily Telegram Bot to improve user experience, performance, and content delivery.
이 문서는 요한복음 데일리 텔레그램 봇의 사용자 경험, 성능, 콘텐츠 전달을 개선하기 위해 변경된 사항을 요약합니다.

## 1. Enhanced Personal Chat UX (Inline Buttons)
## 1. 개인 채팅 UX 개선 (인라인 버튼)

- **Goal**: Replace text commands (`/next`, `/status`) with intuitive buttons.
- **목표**: 텍스트 명령어(`/next`, `/status`)를 직관적인 버튼으로 대체합니다.
- **Implementation**:
- **구현**:
    - Created `src/keyboard_factory.py` to manage inline keyboards.
    - 인라인 키보드를 관리하기 위해 `src/keyboard_factory.py`를 생성했습니다.
    - Updated `src/bot_polling.py` to handle callback queries.
    - 콜백 쿼리를 처리하도록 `src/bot_polling.py`를 업데이트했습니다.
    - Users now see buttons like `[✅ 읽음 완료]`, `[📖 다시 읽기]`, `[📊 내 현황]` below messages.
    - 사용자는 이제 메시지 아래에서 `[✅ 읽음 완료]`, `[📖 다시 읽기]`, `[📊 내 현황]`과 같은 버튼을 볼 수 있습니다.

## 2. Group Chat Interaction (Emoji Reactions)
## 2. 그룹 채팅 상호작용 (이모지 반응)

- **Goal**: Provide feedback when users reply to the bot in group chats.
- **목표**: 그룹 채팅에서 사용자가 봇에게 답장할 때 피드백을 제공합니다.
- **Implementation**:
- **구현**:
    - Added logic in `bot_polling.py` to detect replies to the bot.
    - `bot_polling.py`에 봇에 대한 답장을 감지하는 로직을 추가했습니다.
    - The bot automatically reacts with a 👍 emoji to encourage participation.
    - 봇은 참여를 독려하기 위해 자동으로 👍 이모지로 반응합니다.
    - Improved bot identity detection using `getMe` to work reliably without strict config.
    - 엄격한 설정 없이도 안정적으로 작동하도록 `getMe`를 사용하여 봇 식별 기능을 개선했습니다.

## 3. Performance Optimization (Caching)
## 3. 성능 최적화 (캐싱)

- **Goal**: Reduce Google Sheets API calls and improve response time.
- **목표**: 구글 시트 API 호출을 줄이고 응답 시간을 개선합니다.
- **Implementation**:
- **구현**:
    - Updated `src/plan_repository.py` to load all plan data into memory on startup.
    - 시작 시 모든 플랜 데이터를 메모리에 로드하도록 `src/plan_repository.py`를 업데이트했습니다.
    - `/next` and other commands now respond instantly.
    - `/next` 및 기타 명령어가 이제 즉시 응답합니다.
    - Added `/reload` command to refresh the cache without restarting the bot.
    - 봇을 재시작하지 않고 캐시를 새로 고칠 수 있는 `/reload` 명령어를 추가했습니다.

## 4. Rich Message Format & Content Delivery
## 4. 풍부한 메시지 형식 및 콘텐츠 전달

- **Goal**: Make daily messages more engaging and support multimedia.
- **목표**: 매일 보내는 메시지를 더 매력적으로 만들고 멀티미디어를 지원합니다.
- **Implementation**:
- **구현**:
    - **Verse Text**: Added support for displaying the key verse and reference (from Sheet columns E & F).
    - **성경 구절**: 핵심 구절과 참조(시트 E, F열)를 표시하는 기능을 추가했습니다.
    - **Progress Bar**: Added a dynamic progress indicator (e.g., "진도율 : 6/66 (9% 완료!)").
    - **진도율 표시**: 동적 진도율 표시기(예: "진도율 : 6/66 (9% 완료!)")를 추가했습니다.
    - **Photo Sending**:
    - **사진 전송**:
        - Added support for `Image_URL` in the Google Sheet (Column G).
        - 구글 시트(G열)에 `Image_URL` 지원을 추가했습니다.
        - **Local File Support**: The bot can now upload local image files (starting with `file://` or `/`) directly to Telegram.
        - **로컬 파일 지원**: 봇이 로컬 이미지 파일(`file://` 또는 `/`로 시작)을 텔레그램에 직접 업로드할 수 있습니다.

## 5. Configuration & Debugging Fixes
## 5. 설정 및 디버깅 수정

- **Fixes**:
- **수정 사항**:
    - Resolved `400 Bad Request` errors caused by invalid chat ID formats in `.env`.
    - `.env`의 잘못된 채팅 ID 형식으로 인한 `400 Bad Request` 오류를 해결했습니다.
    - Fixed path resolution for Google Service Account credentials.
    - 구글 서비스 계정 자격 증명의 경로 확인 문제를 수정했습니다.
    - Updated `config.py` to correctly handle commented-out IDs (`#`).
    - 주석 처리된 ID(`#`)를 올바르게 처리하도록 `config.py`를 업데이트했습니다.

## Phase 3: Architecture Refactoring (Completed)
## 3단계: 아키텍처 리팩토링 (완료)

### Key Changes / 주요 변경 사항
1.  **Unified Configuration / 설정 단일화**:
    - Removed `TELEGRAM_GROUP_CHAT_IDS` and `TELEGRAM_GROUP_CONFIG` from `.env` and `config.py`.
    - `.env`와 `config.py`에서 `TELEGRAM_GROUP_CHAT_IDS` 및 `TELEGRAM_GROUP_CONFIG`를 제거했습니다.
    - **Single Source of Truth**: All group configurations (Chat ID, Plan Sheet, Start Date, Timezone) are now exclusively managed via the **Google Sheet (`groups` tab)**.
    - **단일 진실 공급원**: 모든 그룹 설정(채팅 ID, 플랜 시트, 시작일, 타임존)은 이제 **구글 시트(`groups` 탭)**를 통해서만 관리됩니다.
    - `bot_polling.py` and `daily_broadcast.py` now fetch groups dynamically from the sheet.
    - `bot_polling.py`와 `daily_broadcast.py`는 이제 시트에서 그룹을 동적으로 가져옵니다.

2.  **Centralized Constants & Utils / 상수 및 유틸리티 중앙화**:
    - Created `src/constants.py`: Holds all magic strings (sheet names, column headers, messages, emojis).
    - `src/constants.py` 생성: 모든 매직 스트링(시트 이름, 열 헤더, 메시지, 이모지)을 보관합니다.
    - Created `src/utils.py`: Holds helper functions (`convert_google_drive_url`, `parse_chat_destination`).
    - `src/utils.py` 생성: 헬퍼 함수(`convert_google_drive_url`, `parse_chat_destination`)를 보관합니다.

3.  **Hardened Data Layer / 데이터 계층 강화**:
    - `PlanRepository` now uses **Header-based Mapping**.
    - `PlanRepository`는 이제 **헤더 기반 매핑**을 사용합니다.
    - It fetches the first row to find column indices dynamically.
    - 첫 번째 행을 가져와 열 인덱스를 동적으로 찾습니다.
    - This means you can reorder columns in the Google Sheet without breaking the bot, as long as the header names (`Day`, `Ref`, `Title`, etc.) remain correct.
    - 즉, 헤더 이름(`Day`, `Ref`, `Title` 등)만 정확하다면 구글 시트에서 열 순서를 변경해도 봇이 고장 나지 않습니다.

## Verification / 검증

### Phase 2 (Previous) / 2단계 (이전)
- Verified 1:1 flow with inline buttons.
- 인라인 버튼을 사용한 1:1 흐름 검증.
- Verified group message sending with photos and verse text.
- 사진과 성경 구절이 포함된 그룹 메시지 전송 검증.
- Verified emoji reactions in group chats.
- 그룹 채팅에서의 이모지 반응 검증.

### Phase 3 (Architecture) / 3단계 (아키텍처)
- **Automated Test**: Ran `daily_broadcast.py` in `DRY_RUN` mode.
- **자동화 테스트**: `daily_broadcast.py`를 `DRY_RUN` 모드로 실행했습니다.
- **Results / 결과**:
    - Correctly fetched groups from Google Sheet.
    - 구글 시트에서 그룹을 올바르게 가져옴.
    - Correctly loaded plan data using header mapping.
    - 헤더 매핑을 사용하여 플랜 데이터를 올바르게 로드함.
    - Built messages with correct emojis and content.
    - 올바른 이모지와 콘텐츠로 메시지를 생성함.
    - Successfully handled Google Drive image URLs.
    - 구글 드라이브 이미지 URL을 성공적으로 처리함.
