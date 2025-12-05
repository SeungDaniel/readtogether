# Design: User-Group Linking & Anonymous Q&A
# 디자인: 사용자-그룹 연결 및 익명 Q&A

This document outlines the architecture for linking individual users to specific community groups and enabling anonymous Q&A sharing.
이 문서는 개별 사용자를 특정 공동체 그룹에 연결하고 익명 Q&A 공유를 가능하게 하는 아키텍처를 설명합니다.

## 1. The Problem / 문제점
Currently, the bot treats users and groups separately.
현재 봇은 사용자와 그룹을 별개로 취급합니다.
1.  **Context Missing**: In DM (`/next`), the bot doesn't know which group's schedule (start date) the user follows.
2.  **Disconnected Q&A**: If a user asks a question in DM, the community doesn't benefit from the answer.

## 2. Solution Overview / 솔루션 개요
We need a **"Membership System"**.
**"멤버십 시스템"**이 필요합니다.
*   **User <-> Group Link**: Store `group_id` in the user's progress record.
*   **Auto-Registration**: Detect when a user speaks in a group and link them.
*   **Q&A Relay**: Forward DM questions to the linked group anonymously.

## 3. Data Model Changes / 데이터 모델 변경

### `progress` Sheet (Google Sheets)
Add a new column: `Group_ID`
`progress` 시트에 `Group_ID` 열 추가.

| User_ID | Username | Current_Day | Last_Read_At | **Group_ID** |
| :--- | :--- | :--- | :--- | :--- |
| 12345 | john_doe | 5 | 2024-01-01 | **-100123456789** |

## 4. Workflows / 워크플로우

### A. Linking User to Group (멤버십 연결)
**Scenario 1: Auto-Detection (Passive)**
1.  User sends a message in the Group Chat.
2.  Bot detects the message.
3.  Bot checks if this User is already in `progress` sheet.
4.  If yes, update their `Group_ID` to this group's ID.
5.  If no, create a new record.

**Scenario 2: Command (Active)**
1.  User types `/join` in the Group Chat.
2.  Bot replies: "Welcome! You are now linked to [Group Name]."
3.  Bot updates `Group_ID` in `progress` sheet.

### B. Personal Mode Context (개인 모드 컨텍스트)
When user types `/today_group` or asks a question in DM:
1.  Bot looks up `Group_ID` from `progress` sheet.
2.  Bot fetches Group Settings (Start Date, Plan Sheet) from `groups` sheet using `Group_ID`.
3.  Bot calculates the correct "Day" based on that group's schedule.

### C. Anonymous Q&A Sharing (익명 Q&A 공유) - *Future Feature*
1.  **User (DM)**: "Why did Jesus go to Galilee?"
2.  **Bot (DM)**: "That's a great question! Let me think..." (Uses LLM to generate answer)
3.  **Bot (DM)**: "Here is the answer: [Answer Content]"
4.  **Bot (System)**: Checks user's `Group_ID`.
5.  **Bot (Group Chat)**:
    > ❓ **Anonymous Question**
    > "Why did Jesus go to Galilee?"
    >
    > 💡 **Answer**
    > [Answer Content]
    >
    > (Shared from a member's personal study)

## 5. Implementation Steps / 구현 단계
1.  **Update Repository**: Modify `ProgressRepository` to read/write `Group_ID`.
2.  **Implement Linking Logic**: Add logic in `bot_polling.py` to capture `Group_ID` from group messages.
3.  **Update Personal Commands**: Update `/today_group` to use the linked `Group_ID` instead of the first group.
