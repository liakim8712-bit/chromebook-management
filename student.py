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
    st.
