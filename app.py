
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="서울 전광판 광고 필터", layout="wide")

# 구글 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 시트 열기
sheet = client.open_by_key("1_4btUv2PGw0x_TPd1FTkQXd3YV1y2tpJVPFU48ffSf4").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📊 서울 전광판 광고 필터")

# 필터 UI
filters = {}
for col in df.columns:
    options = ["전체"] + sorted(df[col].dropna().unique())
    selected = st.selectbox(f"{col} 선택", options, key=col)
    if selected != "전체":
        filters[col] = selected

# 필터 적용
filtered_df = df.copy()
for col, val in filters.items():
    filtered_df = filtered_df[filtered_df[col] == val]

st.markdown(f"### 🔍 검색 결과: {len(filtered_df)}건")
st.dataframe(filtered_df)

# CSV 다운로드
st.download_button("📥 CSV 다운로드", data=filtered_df.to_csv(index=False), file_name="filtered.csv")

# 데이터 추가 입력창
with st.expander("➕ 새 광고 데이터 추가"):
    new_data = {}
    for col in df.columns:
        new_data[col] = st.text_input(f"{col}", key="input_" + col)
    if st.button("✅ 추가"):
        sheet.append_row([new_data[c] for c in df.columns])
        st.success("✅ 추가 완료! 새로고침 해주세요.")
