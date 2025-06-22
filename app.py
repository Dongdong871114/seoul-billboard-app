import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.write("✅ 앱이 시작되었습니다")

# ✅ Step 1: Streamlit Cloud의 secrets.toml에서 서비스 계정 정보 불러오기
creds_dict = st.secrets["google"]
creds_json = json.dumps(creds_dict)

# ✅ Step 2: Credentials 객체 생성
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json))

# ✅ Step 3: gspread 인증
gc = gspread.authorize(creds)

# ✅ Step 4: 구글 시트 열기 (아래 URL을 사용자의 구글시트 URL로 교체하세요)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/시트ID/edit#gid=0"
worksheet_name = "광고판정보"  # 시트 탭 이름에 맞춰 수정

sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.worksheet(worksheet_name)

# ✅ Step 5: 데이터 불러오기
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# ✅ Step 6: 자동 필터 UI
st.title("📊 서울 광고판 필터")
region = st.selectbox("지역을 선택하세요", ["전체"] + sorted(df["지역"].unique()))
month = st.selectbox("조사월을 선택하세요", ["전체"] + sorted(df["조사월"].unique()))
ad_type = st.selectbox("광고판 구분", ["전체"] + sorted(df["광고판구분"].unique()))

filtered_df = df.copy()
if region != "전체":
    filtered_df = filtered_df[filtered_df["지역"] == region]
if month != "전체":
    filtered_df = filtered_df[filtered_df["조사월"] == month]
if ad_type != "전체":
    filtered_df = filtered_df[filtered_df["광고판구분"] == ad_type]

st.write(f"🔍 총 {len(filtered_df)}건이 조회되었습니다.")
st.dataframe(filtered_df)
