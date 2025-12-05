# Implementation Plan - Phase 5: Parallel Gospels
# 구현 계획 - 5단계: 평행본문

## Goal / 목표
Enhance the personal mode message by displaying "Parallel Gospels" (synoptic verses) instead of the summary. If no parallel verses exist (unique to John), display only the key verse text.
개인 모드 메시지에서 요약 대신 "평행본문"(공관복음 구절)을 표시하도록 개선합니다. 평행본문이 없는 경우(요한복음 독자 기록) 핵심 구절만 표시합니다.

## Proposed Changes / 변경 제안

### 1. Update Constants & Data Layer / 상수 및 데이터 계층 업데이트
#### [MODIFY] [src/constants.py](file:///Users/namseunghyeon/PycharmProjects/PythonProject/John/src/constants.py)
- Add column headers for Parallel Gospels:
    - `COL_MT = "마태 (Mt)"`
    - `COL_MK = "마가 (Mk)"`
    - `COL_LK = "누가 (Lk)"`
- 평행본문용 열 헤더 추가.

#### [MODIFY] [src/plan_repository.py](file:///Users/namseunghyeon/PycharmProjects/PythonProject/John/src/plan_repository.py)
- Update fetch range to include new columns (e.g., `A1:L`).
- Extract `mt`, `mk`, `lk` values in `get_plan_by_day`.
- 데이터 가져오는 범위를 새 열 포함하도록 확장.
- `get_plan_by_day`에서 `mt`, `mk`, `lk` 값 추출.

### 2. Update Message Logic / 메시지 로직 업데이트
#### [MODIFY] [src/bot_polling.py](file:///Users/namseunghyeon/PycharmProjects/PythonProject/John/src/bot_polling.py)
- Update `build_plan_text` function:
    - Check if `mt`, `mk`, `lk` have valid content (not empty, not "-", not "독자 기록").
    - **Condition A (Parallel Exists)**:
        - Display "📖 평행본문 (Parallel Gospels)" section.
        - List valid references: "마태: ...", "마가: ...", "누가: ...".
    - **Condition B (No Parallel / Unique to John)**:
        - Display only the "Verse Text" (Today's Word).
        - Do NOT display "Summary".
    - **Note**: This change applies primarily to `personal=True` mode as requested, but logic can be shared.
- `build_plan_text` 함수 업데이트:
    - `mt`, `mk`, `lk`에 유효한 내용이 있는지 확인.
    - **조건 A (평행본문 있음)**: "📖 평행본문" 섹션 표시 및 구절 나열.
    - **조건 B (평행본문 없음 / 독자 기록)**: "오늘의 말씀"만 표시하고 "요약"은 표시하지 않음.

## Verification Plan / 검증 계획
### Manual Verification / 수동 검증
1.  **Parallel Case**:
    - Check a day with known parallel verses (e.g., Feeding of the 5000).
    - Verify message shows Mt/Mk/Lk references.
    - 평행본문이 있는 날짜(예: 오병이어) 확인. 마태/마가/누가 참조가 나오는지 확인.
2.  **Unique Case**:
    - Check a day unique to John (e.g., Wedding at Cana).
    - Verify message shows ONLY Verse Text, no Summary, no Parallel section.
    - 요한복음 독자 기록 날짜(예: 가나 혼인 잔치) 확인. 오직 말씀 본문만 나오고 요약/평행본문이 없는지 확인.
