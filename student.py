import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], ttl=0)
    df['학급'] = df['학급'].astype(str).str.strip()
    df['기기번호'] = df['기기번호'].astype(str).str.strip()
except Exception as e:
    st.error("구글 스프레드시트 연동 실패! Secrets 주소 설정을 확인하세요.")
    st.stop()

CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]

if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = "전체"

def save_to_gsheet(updated_df):
    conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=updated_df)
    st.cache_data.clear()

with st.sidebar:
    st.header("🏫 학급 선택")
    active_cls = st.selectbox("조회/관리할 학급", CLASSES)
    
    st.markdown(f"**[{active_cls}]** 전체 관리")
    if st.button(f"✨ {active_cls} 전원 '이상 없음' 초기화", use_container_width=True):
        df.loc[df['학급'] == active_cls, '상태'] = "이상 없음"
        df.loc[df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_to_gsheet(df)
        st.success(f"{active_cls} 학급 초기화 완료!")
        st.rerun()
    
    st.divider()
    
    st.header("🛠️ 개별 상태 수정")
    cls_devices = df[df['학급'] == active_cls]
    
    if cls_devices.empty:
        st.warning(f"{active_cls} 학급에 할당된 크롬북 데이터가 구글 시트에 없습니다.")
    else:
        device_options = cls_devices['기기번호'].tolist()
        device_labels = {row['기기번호']: f"[{row['기기번호']}] {int(float(row['번호']))}번 {row['이름']}" for _, row in cls_devices.iterrows()}
        
        with st.form("edit_form"):
            target_id = st.selectbox("대상 크롬북(CEU)", device_options, format_func=lambda x: device_labels.get(x, x))
            current_row = df[df['기기번호'] == target_id].iloc[0]
            
            new_status = st.radio("상태 변경", ["이상 없음", "대여 중", "파손/점검", "분실"], 
                                   index=["이상 없음", "대여 중", "파손/점검", "분실"].index(current_row['상태']))
            new_note = st.text_input("특이사항", value=str(current_row['특이사항']) if pd.notna(current_row['특이사항']) else "-")
            
            if st.form_submit_button("변경사항 저장"):
                idx = df[df['기기번호'] == target_id].index[0]
                df.at[idx, '상태'] = new_status
                df.at[idx, '특이사항'] = new_note if new_note else "-"
                df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_to_gsheet(df)
                st.success(f"{current_row['이름']} 학생 기기 수정 완료!")
                st.rerun()

st.title("💻 크롬북 통합 현황판")

col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 기기", f"{len(df)}대")
col2.metric("🟢 정상", f"{len(df[df['상태']=='이상 없음'])}대")
col3.metric("🏠 대여중", f"{len(df[df['상태']=='대여 중'])}대")
col4.metric("🚨 점검/분실", f"{len(df[df['상태'].isin(['파손/점검', '분실'])])}대")

st.divider()

f1, f2, f3, f4, _ = st.columns([1,1,1,1,2])
if f1.button("전체 보기", use_container_width=True): st.session_state.filter_mode = "전체"
if f2.button("🟢 정상만", use_container_width=True): st.session_state.filter_mode = "이상 없음"
if f3.button("🏠 대여중만", use_container_width=True): st.session_state.filter_mode = "대여 중"
if f4.button("🚨 점검필요", use_container_width=True): st.session_state.filter_mode = "점검필요"

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