# Sheet Names
PLAN_SHEET_NAME = "plan"
PROGRESS_SHEET_NAME = "progress"
GROUPS_SHEET_NAME = "groups"
LOG_SHEET_NAME = "logs"

# Column Headers (Plan Sheet)
COL_DAY = "Day"
COL_REF = "Ref"
COL_TITLE = "Title"
COL_SUMMARY = "Summary"
COL_VERSE_TEXT = "Verse_Text"
COL_VERSE_REF = "Verse_Ref"
COL_IMAGE_URL = "Image_URL"
COL_YOUTUBE_LINK = "Youtube_Link"
COL_MT = "마태 (Mt)"
COL_MK = "마가 (Mk)"
COL_LK = "누가 (Lk)"

# Column Headers (Groups Sheet)
COL_CHAT_ID = "chat_id"
COL_PLAN_SHEET = "plan_sheet"
COL_START_DATE = "start_date"
COL_TIMEZONE = "timezone"

# Messages
MSG_WELCOME = (
    "안녕하세요! 요한복음 봇입니다. 🙌\n\n"
    "개인 퀘스트를 시작하려면 /start_john 을 입력해주세요."
)
MSG_ALREADY_STARTED = (
    "이미 요한복음 퀘스트를 진행 중입니다. 😊\n\n"
    "- 현재 진행 단계: DAY {current_day}\n\n"
    "아래 버튼을 눌러 계속 진행해보세요."
)
MSG_QUEST_START = (
    "요한복음 데일리 퀘스트를 시작합니다. ✨\n"
    "지금부터 당신의 속도로, 1일차부터 차근차근 함께 읽을게요.\n\n"
    "준비가 되셨다면 아래 버튼을 눌러 첫 퀘스트를 받아보세요!"
)
MSG_NO_QUEST = "더 이상 준비된 퀘스트가 없습니다. 축하합니다, 완주하셨습니다! 🎉"
MSG_NOT_STARTED = "아직 요한복음 퀘스트를 시작하지 않으셨습니다. /start_john 으로 시작할 수 있어요."
MSG_STATUS_HEADER = "🔎 나의 요한복음 퀘스트 현황\n\n"
MSG_STATUS_BODY = "- 완료한 퀘스트: DAY {finished_day}\n- 다음 퀘스트: DAY {next_day} – {ref} ({title})"
MSG_STATUS_FINISHED = "- 완료한 퀘스트: DAY {finished_day}\n이미 준비된 모든 퀘스트를 완료하셨습니다. 🎉"

# Emojis
EMOJI_REACTION = "👍"
EMOJI_MAP = "🗺️"
EMOJI_COMPASS = "🧭"
EMOJI_HEADPHONE = "🎧"
EMOJI_BOOK = "📖"
EMOJI_RAINBOW = "🌈"
