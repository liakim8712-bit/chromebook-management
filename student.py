import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")

DB_FILE = "chromebook_master_db.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]

# 상북중 명렬 데이터
ROSTERS = {
    "1-1": (
        "c020_김동율,c031_김민석,c016_김어진,c008_김타냐,c102_노아,c011_박하민,"
        "c128_손연아,c014_양승호,c022_원상현,c033_윤소연,c007_이성제,c026_이정후,"
        "c124_이하경,c034_정채준,c027_주선우,c017_최예빈,c010_최재혁,c021_허민서,c125_이나예"
    ),
    "1-2": (
        "c018_김가람,114_김들,c009_김서후,c029_김재빈,c112_박마루,c025_박지은,"
        "c013_배서윤,c003_원세준,c117_윤하정,c037_이예원,c123_이준환,c129_임시우,"
        "c048_장주혁,c028_정유진,c103_정현석,c032_최아영,c070_최은지,c135_허동혁,c073_황승미"
    ),
    "2-1": (
        "c062_ANSHENGBIN,c045_곽고은,c126_김가림,c047_김리안,c012_김무성,c038_김미설,"
        "c023_김소현,c087_김태은,c051_박예은,c078_신민준,c035_양지연,c063_오동건,"
        "c080_윤채환,c076_윤현정,c060_이나원,c001_이대현,c042_이아영,c054_이정희,"
        "c122_정가인,c069_정민기,c065_진정한,c055_허동진"
    ),
    "2-2": (
        "c050_강주원,c071_고대균,c043_곽유찬,c058_김건희,c130_김경은,c074_김대우,"
        "c030_김도형,c039_김라온,c053_김민성,c127_김민현,c059_김시현,c040_김지후,"
        "c072_박소영,c068_박태양,c077_백재욱,c061_손예림,c079_송다임,c064_이지향,"
        "c067_이혜진,c096_이효아,c049_정다윤,c132_정승현,c057_정하린"
    ),
    "3-1": (
        "c101_강보민,c088_김가온,c105_김미래,c104_김민건,c002_김민준,c139_김연호,"
        "c092_김은화,c081_남혁주,c118_문시윤,c085_박민체,c111_원영준,c110_원태경,"
        "c084_유도겸,c097_이지우,c120_이지윤,c083_전서원,c116_정수연,c004_정아단,c137_진유빈"
    ),
    "3-2": (
        "c005_KOONKOKKRUAD THANAWUT,c089_공지연,c090_김나로,c091_김연서,c106_김지호,"
        "c133_김채은,c113_남세빈,c086_문채혁,c093_박수경,c108_서다울,c109_서지원,"
        "c094_송요찬,c134_신하원,c095_이규민,c136_이은수,c115_이해린,c082_정혜빈,"
        "c100_주승현,c099_진채원,c121_이온리"
    )
}

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    data = []
    for cls, students in ROSTERS.items():
        for idx, student in enumerate(students.split(',')):
            parts = student.split('_')
            data.append({
                "기기번호": parts[0],
                "학급": cls,
                "번호": idx + 1,
                "이름": parts[1],
                "상태": "이상 없음",
                "특이사항": "-",
                "최종수정": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = "전체"

def save_data():
    st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- UI 레이아웃 ---
with st.sidebar:
    st.header("🏫 학급 선택")
    active_cls = st.selectbox("조회/관리할 학급", CLASSES)
    
    st.markdown(f"**[{active_cls}]** 전체 관리")
    if st.button(f"✨ {active_cls} 전원 '이상 없음' 초기화", use_container_width=True):
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '상태'] = "이상 없음"
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '특이사항'] = "-"
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_data()
        st.success(f"{active_cls} 학급 초기화 완료!")
        st.rerun()
    
    st.divider()
    
    st.header("🛠️ 개별 상태 수정")
    cls_devices = st.session_state.df[st.session_state.df['학급'] == active_cls]
    
    if not cls_devices.empty:
        device_options = cls_devices['기기번호'].tolist()
        device_labels = {row['기기번호']: f"[{row['기기번호']}] {row['번호']}번 {row['이름']}" for _, row in cls_devices.iterrows()}
        
        target_id = st.selectbox("대상 크롬북(CEU)", device_options, format_func=lambda x: device_labels.get(x, x))
        current_row = st.session_state.df[st.session_state.df['기기번호'] == target_id].iloc[0]
        
        new_status = str(current_row['상태'])
        status_list = ["이상 없음", "대여 중", "파손/점검", "분실"]
        status_index = status_list.index(new_status) if new_status in status_list else 0
        
        new_status = st.radio("상태 변경", status_list, index=status_index)
        
        # placeholder 가이드 글자 자동 비우기 로직
        placeholder_val = ""
        current_note_value = str(current_row['특이사항']) if current_row['특이사항'] != "-" else ""
        
        if new_status == "대여 중" and "반납예정일" not in current_note_value:
            placeholder_val = "[반납예정일: YYYY-MM-DD]"
            current_note_value = "" 

        new_note = st.text_input("특이사항", value=current_note_value, placeholder=placeholder_val)
        
        if st.button("💾 변경사항 저장", use_container_width=True):
            final_note = new_note if new_note else (placeholder_val if placeholder_val else "-")
            if new_status == "대여 중" and not new_note:
                st.error("⚠️ 대여 중일 때는 반드시 반납 예정 날짜를 입력해 주세요!")
            else:
                idx = st.session_state.df[st.session_state.df['기기번호'] == target_id].index[0]
                st.session_state.df.at[idx, '상태'] = new_status
                st.session_state.df.at[idx, '특이사항'] = final_note
                st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_data()
                st.success(f"{current_row['이름']} 학생 기기 수정 완료!")
                st.rerun()

st.title("💻 상북중 크롬북 통합 현황판")

df = st.session_state.df.copy()

# --- 💡 대시보드용 실시간 N 마크 판단 로직 ---
df['최종수정_dt'] = pd.to_datetime(df['최종수정'], format="%Y-%m-%d %H:%M")

has_recent_rent = False
has_recent_damage = False

for idx, row in df.iterrows():
    # 5분 이내에 수정 이력이 있는 기기 감지
    if datetime.now() - row['최종수정_dt'] < timedelta(minutes=5):
        if row['상태'] == "대여 중":
            has_recent_rent = True
        elif row['상태'] in ["파손/점검", "분실"]:
            has_recent_damage = True

rent_label = "🏠 대여중 N" if has_recent_rent else "🏠 대여중"
damage_label = "🚨 점검/분실 N" if has_recent_damage else "🚨 점검/분실"

# 대시보드 지표 출력 (요청하신 글자 옆에 N 연동 완료)
col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 기기", f"{len(df)}대")
col2.metric("🟢 정상", f"{len(df[df['상태']=='이상 없음'])}대")
col3.metric(rent_label, f"{len(df[df['상태']=='대여 중'])}대")
col4.metric(damage_label, f"{len(df[df['상태'].isin(['파손/점검', '분실'])])}대")

st.divider()

f1, f2, f3, f4, _ = st.columns([1,1,1,1,2])
if f1.button("전체 보기", use_container_width=True): st.session_state.filter_mode = "전체"
if f2.button("🟢 정상만", use_container_width=True): st.session_state.filter_mode = "이상 없음"
if f3.button("🏠 대여중만", use_container_width=True): st.session_state.filter_mode = "대여 중"
if f4.button("🚨 점검필요", use_container_width=True): st.session_state.filter_mode = "점검필요"

# 필터링 적용 및 테이블 노출
view_df = df.copy()
if st.session_state.filter_mode == "이상 없음":
    view_df = view_df[view_df['상태'] == "이상 없음"]
elif st.session_state.filter_mode == "대여 중":
    view_df = view_df[view_df['상태'] == "대여 중"]
elif st.session_state.filter_mode == "점검필요":
    view_df = view_df[view_df['상태'].isin(["파손/점검", "분실"])]

view_df = view_df[["기기번호", "학급", "번호", "이름", "상태", "특이사항", "최종수정"]]

def style_status(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4; color: #22543d'
    elif row['상태'] == "대여 중": color = 'background-color: #ebf8ff; color: #2a4365'
    elif row['상태'] in ["파손/점검", "분실"]: color = 'background-color: #fff5f5; color: #742a2a; font-weight: bold'
    return [color] * len(row)

st.dataframe(
    view_df.style.apply(style_status, axis=1), 
    use_container_width=True, 
    hide_index=True,
    height=600
)
