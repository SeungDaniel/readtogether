# 향후 발전 계획 (Roadmap)

## ✅ 완료된 작업 (2026-02)

### Phase 1: 구조 단순화
- [x] 폴링 봇 제거 → `archive/`로 이동
- [x] Daily Broadcast + 읽음 인증 하이브리드 모델

### Phase 2: Multi-Book 지원
- [x] `book_registry.py` 생성
- [x] 요한복음 (66일) + 이사야 (94일)

### Phase 3: 읽음 인증 기능
- [x] 인라인 버튼 `[✅ 읽었어요]` 추가
- [x] Webhook 기반 `callback_handler.py`
- [x] Google Sheets `confirmations` 시트 연동

---

## 🚧 진행 예정

### Phase 4: 배포 및 안정화
- [ ] Webhook URL 등록 및 서버 배포
- [ ] Cron + Webhook 동시 운영 검증
- [ ] 에러 모니터링 추가

### Phase 5: UX 개선
- [ ] **연속 읽기 배지**: "3일 연속! 🔥", "7일 연속! 🏆"
- [ ] **주간 리포트**: 공동체 진도율 자동 발송
- [ ] **리마인더**: 읽지 않은 사용자에게 저녁 알림

### Phase 6: 관리자 웹 UI 🆕
- [ ] **Flask/FastAPI 기반 웹 페이지**
- [ ] **관리자 로그인**: Telegram/Google OAuth
- [ ] **그룹 설정 관리**:
  - 발송 시간 변경
  - 책 선택 (드롭다운)
  - 시작일 설정 (달력 UI)
- [ ] **통계 대시보드**: 읽음 인증 현황

### Phase 7: 데이터 고도화
- [ ] Google Sheets → SQLite 마이그레이션 (성능 개선)

---

## 📖 새 책 추가 방법

### Step 1: 데이터 준비
```csv
# data/[book]_plan.csv
Day,Ref,Title,Verse_Text,Verse_Ref,Image_URL,Youtube_Link
1,마태복음 1:1-17,예수님의 족보,...
```

### Step 2: book_registry.py에 등록
```python
"matthew": {
    "id": "matthew",
    "name_ko": "마태복음",
    "total_days": 100,
    "sheet_name": "plan_matthew",
    "game_link": "",
},
```

### Step 3: Google Sheets
1. `plan_matthew` 탭 생성 + CSV 붙여넣기
2. `groups` 시트에서 `plan_sheet`를 `plan_matthew`로 변경

---

## 📅 책 확장 계획

| 순서 | 책 | 예상 일수 | 상태 |
|------|-----|----------|------|
| 1 | 요한복음 | 66일 | ✅ 운영중 |
| 2 | 이사야 | 94일 | ✅ 플랜 준비완료 |
| 3 | 마태복음 | TBD | 📋 예정 |
| 4 | 로마서 | TBD | 📋 예정 |
