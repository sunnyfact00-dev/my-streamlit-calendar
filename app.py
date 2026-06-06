import calendar
from datetime import datetime
import streamlit as st

# 페이지 설정 (넓은 화면 모드)
st.set_page_config(layout="wide")

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
        .cal-table th, .cal-table td { border: 1px solid #e0e0e0; vertical-align: top; padding: 5px; height: 110px; }
        .cal-header { font-size: 22px; font-weight: bold; text-align: center; margin-top: 10px; color: #333; }
        .th-sun { color: red; text-align: center; font-weight: bold; background: #fafafa; }
        .th-sat { color: blue; text-align: center; font-weight: bold; background: #fafafa; }
        .th-week { color: #333; text-align: center; font-weight: bold; background: #fafafa; }
        .day-num { font-weight: bold; font-size: 14px; margin-bottom: 5px; color: #333; }
        .today-box { background-color: #FFF9C4 !important; border: 2px solid #FBC02D !important; }
        .event-completed { color: #2E7D32; font-size: 12px; margin-top: 3px; font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;}
        .event-pending { color: #424242; font-size: 12px; margin-top: 3px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;}
        .period-box { font-size: 11px; padding: 3px 5px; margin-bottom: 2px; border-radius: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: bold; height: 16px; line-height: 16px; }
        .period-box-empty { height: 22px; margin-bottom: 2px; border-radius: 3px; }
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
                            html += f'<div class="period-box" style="background-color: {color_set["bg"]}; color: {color_set["text"]};">{display_title}</div>'
                        else:
                            html += f'<div class="period-box-empty" style="background-color: {color_set["bg"]};"></div>'

            # 일반 일정 렌더링
            for d_event in st.session_state.my_daily_events:
                if d_event.get("year") == year and d_event.get("month") == month:
                    if d_event["day"] == day:
                        if d_event["completed"]:
                            html += f'<div class="event-completed">✓ {d_event["title"]}</div>'
                        else:
                            html += f'<div class="event-pending">· {d_event["title"]}</div>'

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

# -------------------------------------------------------------
# 5. 실시간 일정 완료 여부 토글(체크박스) 영역
# -------------------------------------------------------------
st.subheader(f"✅ {selected_year}년 {selected_month}월 일정 토글 관리")

daily_items = [e for e in st.session_state.my_daily_events if e.get("year") == selected_year and e.get("month") == selected_month]
period_items = [e for e in st.session_state.my_period_events if e.get("year") == selected_year and e.get("month") == selected_month]

if not daily_items and not period_items:
    st.info("이 달에 등록된 일정이 없습니다. 아래에서 일정을 추가해 보세요!")
else:
    t_col1, t_col2 = st.columns(2)

    for idx, item in enumerate(daily_items):
        target_col = t_col1 if idx % 2 == 0 else t_col2
        with target_col:
            new_val = st.checkbox(f"[일반] {item['day']}일 - {item['title']}", value=item["completed"], key=f"chk_d_{item['day']}_{idx}")
            if new_val != item["completed"]:
                item["completed"] = new_val
                st.rerun()

    for idx, item in enumerate(period_items):
        target_col = t_col1 if idx % 2 == 0 else t_col2
        with target_col:
            new_val = st.checkbox(f"[기간] {item['start']}일~{item['end']}일 - {item['title']}", value=item["completed"], key=f"chk_p_{item['start']}_{idx}")
            if new_val != item["completed"]:
                item["completed"] = new_val
                st.rerun()

st.divider()

# -------------------------------------------------------------
# 6. 새 일정 등록 영역 (실시간 반응을 위해 선택상자를 Form 밖으로 배치)
# -------------------------------------------------------------
st.subheader("➕ 새 일정 등록하기")

_, last_day = calendar.monthrange(selected_year, selected_month)

# [수정 핵심] 실시간 리렌더링을 위해 일정 종류 선택을 Form 외부(위쪽)로 뺐습니다.
col_iy, col_im, col_type = st.columns([1, 1, 2])
with col_iy:
    in_year = st.selectbox("등록 연도", list(range(2020, 2031)), index=list(range(2020, 2031)).index(selected_year))
with col_im:
    in_month = st.selectbox("등록 월", list(range(1, 13)), index=selected_month - 1)
with col_type:
    type_select = st.selectbox('일정 종류', ['일반 일정(하루)', '기간 일정'])

# 실제 입력 폼 시작
with st.form(key='event_form', clear_on_submit=True):
    title_input = st.text_input('일정 제목', placeholder='일정 제목을 입력하세요')

    col_s, col_e, col_c = st.columns([2, 2, 1])
    with col_s:
        start_label = '날짜(시작일)' if type_select == '기간 일정' else '날짜'
        start_input = st.number_input(start_label, min_value=1, max_value=last_day, value=1)
    with col_e:
        # 이제 외부 선택상자 변경에 따라 종료일 칸이 즉시 활성화/비활성화됩니다!
        if type_select == '기간 일정':
            end_input = st.number_input('종료일(기간용)', min_value=1, max_value=last_day, value=int(start_input))
        else:
            st.number_input('종료일(기간용)', min_value=0, max_value=0, value=0, disabled=True)
            end_input = start_input
    with col_c:
        st.write("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
        completed_check = st.checkbox('즉시 완료 처리')

    add_button = st.form_submit_button('🚀 일정 추가하기', type='primary', use_container_width=True)

    if add_button:
        title = title_input.strip()

        if not title:
            st.error("⚠ 일정 제목을 입력해 주세요.")
        elif type_select == '기간 일정' and start_input > end_input:
            st.error("⚠ 시작일이 종료일보다 늦을 수 없습니다.")
        else:
            if type_select == '일반 일정(하루)':
                st.session_state.my_daily_events.append({
                    "year": in_year,
                    "month": in_month,
                    "day": int(start_input),
                    "title": title,
                    "completed": completed_check
                })
            else:
                st.session_state.my_period_events.append({
                    "year": in_year,
                    "month": in_month,
                    "start": int(start_input),
                    "end": int(end_input),
                    "title": title,
                    "completed": completed_check
                })
            st.toast("일정이 성공적으로 추가되었습니다!")
            st.rerun()

st.divider()

# -------------------------------------------------------------
# 7. 메인 달력 출력
# -------------------------------------------------------------
render_calendar(selected_year, selected_month)
