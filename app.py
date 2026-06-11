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
    st.session_state.my_period_events = []

if 'my_daily_events' not in st.session_state:
    st.session_state.my_daily_events = []

# -------------------------------------------------------------
# 2. 색상 팔레트 정의 (기간별 구분을 위한 파스텔톤 7종)
# -------------------------------------------------------------
PERIOD_COLORS = [
    {"bg": "#E3F2FD", "text": "#0D47A1"},
    {"bg": "#E8F5E9", "text": "#1B5E20"},
    {"bg": "#FFF3E0", "text": "#E65100"},
    {"bg": "#F3E5F5", "text": "#4A148C"},
    {"bg": "#FCE4EC", "text": "#880E4F"},
    {"bg": "#E0F7FA", "text": "#006064"},
    {"bg": "#FFFDE7", "text": "#F57F17"}
]

COMPLETED_COLOR = {"bg": "#ECEFF1", "text": "#546E7A"}

# -------------------------------------------------------------
# 3. 달력 렌더링 함수 (CSS 호환성 강화 버전)
# -------------------------------------------------------------
def render_calendar(year, month):
    now = datetime.now()

    # 호환성을 위해 폰트 지정을 안전하게 바꾸고 테이블이 깨지지 않도록 보완
    style = """
    <style>
        .cal-wrapper { width: 100%; margin-top: 20px; margin-bottom: 20px; }
        .cal-table { border-collapse: collapse; width: 100%; table-layout: fixed; background-color: #ffffff; }
        .cal-table th, .cal-table td { border: 1px solid #dee2e6; vertical-align: top; padding: 8px; height: 120px; }
        .cal-header { font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 15px; color: #212529; }
        .th-sun { color: #dc3545; text-align: center; font-weight: bold; background: #f8f9fa; }
        .th-sat { color: #0d6efd; text-align: center; font-weight: bold; background: #f8f9fa; }
        .th-week { color: #212529; text-align: center; font-weight: bold; background: #f8f9fa; }
        .day-num { font-weight: bold; font-size: 15px; margin-bottom: 8px; color: #212529; }
        .today-box { background-color: #fff3cd !important; border: 2px solid #ffc107 !important; }
        .event-completed { color: #6c757d; text-decoration: line-through; font-size: 12px; margin-top: 4px; font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;}
        .event-pending { color: #212529; font-size: 12px; margin-top: 4px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;}
        .period-box { font-size: 11px; padding: 4px 6px; margin-bottom: 3px; border-radius: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: bold; height: 20px; line-height: 12px; }
        .period-box-empty { height: 20px; margin-bottom: 3px; border-radius: 4px; font-size: 11px; padding: 4px 6px; line-height: 12px; opacity: 0.6; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
    </style>
    """

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    html = f'{style}<div class="cal-wrapper">'
    html += f'<div class="cal-header">📅 {year}년 {month}월 캘린더</div>'
    html += '<table class="cal-table">'
    html += '<thead><tr><th class="th-sun">일</th><th class="th-week">월</th><th class="th-week">화</th><th class="th-week">수</th><th class="th-week">목</th><th class="th-week">금</th><th class="th-sat">토</th></tr></thead>'
    html += '<tbody>'

    for week in month_days:
        html += '<tr>'
        for idx, day in enumerate(week):
            if day == 0:
                html += '<td style="background-color:#f8f9fa;"></td>'
                continue

            is_today = (year == now.year and month == now.month and day == now.day)
            td_class = ' class="today-box"' if is_today else ''

            day_style = ""
            if idx == 0: day_style = "color: #dc3545;"
            elif idx == 6: day_style = "color: #0d6efd;"

            html += f'<td{td_class}><div class="day-num" style="{day_style}">{day}</div>'

            # 기간 일정 렌더링
            for p_idx, p_event in enumerate(st.session_state.my_period_events):
                if p_event.get("year") == year and p_event.get("month") == month:
                    if p_event["start"] <= day <= p_event["end"]:
                        if p_event.get("completed", False):
                            color_set = COMPLETED_COLOR
                        else:
                            color_set = PERIOD_COLORS[p_idx % len(PERIOD_COLORS)]

                        if day == p_event["start"]:
                            display_title = f"✓ {p_event['title']}" if p_event.get("completed", False) else p_event["title"]
                            html += f'<div class="period-box" style="background-color: {color_set["bg"]}; color: {color_set["text"]};" title="{p_event["title"]}">{display_title}</div>'
                        else:
                            display_title = f"→ {p_event['title']}"
                            html += f'<div class="period-box-empty" style="background-color: {color_set["bg"]}; color: {color_set["text"]};" title="{p_event["title"]}">{display_title}</div>'

            # 일반 일정 렌더링
            for d_event in st.session_state.my_daily_events:
                if d_event.get("year") == year and d_event.get("month") == month:
                    if d_event["day"] == day:
                        if d_event.get("completed", False):
                            html += f'<div class="event-completed" title="{d_event["title"]}">✓ {d_event["title"]}</div>'
                        else:
                            html += f'<div class="event-pending" title="{d_event["title"]}">· {d_event["title"]}</div>'

            html += '</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'

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

# 무조건 강제로 먼저
