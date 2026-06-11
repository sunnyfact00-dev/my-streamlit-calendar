import calendar
from datetime import datetime
import streamlit as st
import uuid

# 페이지 설정 (넓은 화면 모드)
st.set_page_config(layout="wide", page_title="스마트 일정 관리 플래너")

# -------------------------------------------------------------
# 1. 글로벌 데이터 저장소 (Streamlit Session State 이용)
# -------------------------------------------------------------
if 'my_period_events' not in st.session_state:
    st.session_state.my_period_events = []  # 기간 일정 저장소

if 'my_daily_events' not in st.session_state:
    st.session_state.my_daily_events = []   # 일반 일정 저장소

# -------------------------------------------------------------
# 2. 색상 팔레트 정의 (기간별 구분을 위한 파스텔톤 7종)
# -------------------------------------------------------------
PERIOD_COLORS = [
    {"bg": "#E3F2FD", "text": "#0D47A1"},  # 블루
    {"bg": "#E8F5E9", "text": "#1B5E20"},  # 그린
    {"bg": "#FFF3E0", "text": "#E65100"},  # 오렌지
    {"bg": "#F3E5F5", "text": "#4A148C"},  # 퍼플
    {"bg": "#FCE4EC", "text": "#880E4F"},  # 핑크
    {"bg": "#E0F7FA", "text": "#006064"},  # 시안
    {"bg": "#FFFDE7", "text": "#F57F17"}   # 옐로우
]

COMPLETED_COLOR = {"bg": "#ECEFF1", "text": "#546E7A"}

# -------------------------------------------------------------
# 3. 달력 렌더링 함수
# -------------------------------------------------------------
def render_calendar(year, month):
    now = datetime.now()

    style = """
    <style>
        .cal-table { border-collapse: collapse; width: 100%; font-family: 'Malgun Gothic', sans-serif; table-layout: fixed; margin-top: 15px;}
        .cal-table th, .cal-table td { border: 1px solid #e0e0e0; vertical-align: top; padding: 5px; height: 120px; }
        .cal-header { font-size: 24px; font-weight: bold; text-align: center; margin-top: 10px; color: #333; }
        .th-sun { color: red; text-align: center; font-weight: bold; background: #fafafa; }
        .th-sat { color: blue; text-align: center; font-weight: bold; background: #fafafa; }
        .th-week { color: #333; text-align: center; font-weight: bold; background: #fafafa; }
        .day-num { font-weight: bold; font-size: 14px; margin-bottom: 5px; color: #333; }
        .today-box { background-color: #FFF9C4 !important; border: 2px solid #FBC02D !important; }
        .event-completed { color: #9E9E9E; text-decoration: line-through; font-size: 12px; margin-top: 3px; font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;}
        .event-pending { color: #424242; font-size: 12px; margin-top: 3px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;}
        .period-box { font-size: 11px; padding: 3px 5px; margin-bottom: 2px; border-radius: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: bold; height: 18px; line-height: 18px; }
        .period-box-empty { height: 18px; margin-bottom: 2px; border-radius: 3px; font-size: 11px; padding: 3px 5px; line-height: 18px; opacity: 0.5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
    </style>
    """

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    html = f'{style}<div class="cal-header">📅 {year}년 {month}월 캘린더</div>'
    html += '<table class="cal-table">'
    html += '<tr><th class="th-sun">일</th><th class="th-week">월</th><th class="th-week">화</th><th class="th-week">수</th><th class="th-week">목</th><th class="th-week">금</th><th class="th-sat">토</th></tr>'

    for week in month_days:
        html += '<tr>'
        for idx, day in enumerate(week):
            if day == 0:
                html += '<td style="background:#f9f9f9;"></td>'
                continue

            is_today = (year == now.year and month == now.month and day == now.day)
            td_class = ' class="today-box"' if is_today else ''

            day_style = ""
            if idx == 0: day_style = "color: red;"
            elif idx == 6: day_style = "color: blue;"

            html += f'<td{td_class}><div class="day-num" style="{day_style}">{day}</div>'

            # 기간 일정 렌더링
            for p_idx, p_event in enumerate(st.session_state.my_period_events):
                if p_event.get("year") == year and p_event.get("month") == month:
                    if p_event["start"] <= day <= p_event["end"]:
                        if p_event["completed"]:
                            color_set = COMPLETED_COLOR
                        else:
                            color_set = PERIOD_COLORS[p_idx % len(PERIOD_COLORS)]

                        if day == p_event["start"]:
                            display_title = f"✓ {p_event['title']}" if p_event["completed"] else p_event["title"]
                            html += f'<div class="period-box" style="background-color: {color_set["bg"]}; color: {color_set["text"]};" title="{p_event["title"]}">{display_title}</div>'
                        else:
                            display_title = f"→ {p_event['title']}"
                            html += f'<div class="period-box-empty" style="background-color: {color_set["bg"]}; color: {color_set["text"]};" title="{p_event["title"]}">{display_title}</div>'

            # 일반 일정 렌더링
            for d_event in st.session_state.my_daily_events:
                if d_event.get("year") == year and d_event.get("month") == month:
                    if d_event["day"] == day:
                        if d_event["completed"]:
                            html += f'<div class="event-completed" title="{d_event["title"]}">✓ {d_event["title"]}</div>'
                        else:
                            html += f'<div class="event-pending" title="{d_event["title"]}">· {d_event["title"]}</div>'

            html += '</td>'
        html += '</tr>'
    html += '</table>'

    st.markdown(html, unsafe_allow_html=True)


# -------------------------------------------------------------
# 4. 상단 대시보드 및 조회 제어 영역
# -------------------------------------------------------------
st.title("📆 스마트 일정 관리 플래너")

col_year, col_month, col_reset = st.columns([2, 2, 2])

with col_year:
    selected_year = st.selectbox("📅 조회 연도", list(range(2020, 2031)), index=6) # 기본값 2026

with col_month:
    selected_month = st.selectbox("📆 조회 월", list(range(1, 13)), index=5) # 기본값 6

with col_reset:
    st.write("<div style='padding-top: 24px;'></div>", unsafe_allow_html=True)
    if st.button("🗑 모든 일정 초기화", type="secondary", use_container_width=True):
        st.session_state.my_period_events = []
        st.session_state.my_daily_events = []
        st.toast("모든 일정이 초기화되었습니다!")
        st.rerun()

st.divider()

# ✨ 개선: 사용자가 일정을 바로 확인할 수 있도록 캘린더 화면을 상단에 먼저 렌더링합니다.
render_calendar(selected_year, selected_month)

st.divider()

# -------------------------------------------------------------
# 5. 실시간 일정 관리 (토글 및 개별 삭제) 영역
# -------------------------------------------------------------
st.subheader(f"✅ {selected_year}년 {selected_month}월 일정 편집 및 관리")

daily_items = [e for e in st.session_state.my_daily_events if e.get("year") == selected_year and e.get("month") == selected_month]
period_items =
