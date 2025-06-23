import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 앱 시작 확인용 로그
st.write("✅ 앱이 시작되었습니다")

# ✅ Streamlit secrets 인증 방식
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["google"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
client = gspread.authorize(creds)

# ✅ 구글시트에서 데이터 로드
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit")
worksheet = spreadsheet.worksheet("DATA")  # 시트명 정확히 'DATA'
data = pd.DataFrame(worksheet.get_all_records())

st.title("🎉서울 주요 전광판 광고주 조사🎉")

# ✅ 필터 항목 정의
filter_columns = [
    "조사월",
    "위치",
    "빌딩&전광판",
    "업종",
    "제품&브랜드",
    "광고대행사(연락처) ",
    "미디어렙사(연락처)",
    "광고주(연락처)",
    "해외본사"
]

filters = {}
for col in filter_columns:
    if col in data.columns:
        options = sorted(data[col].astype(str).unique())
        filters[col] = st.multiselect(col, ["전체"] + options)

# ✅ 필터 적용
filtered_data = data.copy()
for col, selected in filters.items():
    if selected and "전체" not in selected:
        filtered_data = filtered_data[filtered_data[col].astype(str).isin(selected)]

# ✅ 필터 결과 출력
st.markdown("### 🔍 필터 결과")
st.dataframe(filtered_data, use_container_width=True)

# ✅ CSV 다운로드
st.download_button(
    label="📥 필터 결과 CSV 다운로드",
    data=filtered_data.to_csv(index=False).encode('utf-8-sig'),
    file_name="filtered_billboard_data.csv",
    mime="text/csv"
)

# ✅ 📈 월별 광고주별 광고 수 (필터 적용)
st.markdown("### 📈 월별 광고주별 광고 수")
month_options = sorted(data["조사월"].astype(str).unique())
selected_month = st.selectbox("조사월 선택", ["전체"] + month_options)

industry_options = sorted(data["업종"].astype(str).unique())
selected_industry = st.selectbox("업종 선택", ["전체"] + industry_options)

stat_data = data.copy()
if selected_month != "전체":
    stat_data = stat_data[stat_data["조사월"].astype(str) == selected_month]
if selected_industry != "전체":
    stat_data = stat_data[stat_data["업종"].astype(str) == selected_industry]

monthly_advertisers = stat_data.groupby(["조사월", "광고주(연락처)"]).size().reset_index(name="건수")
st.dataframe(monthly_advertisers.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

# ✅ 🌍 월별 해외본사 광고 수 (필터 적용)
st.markdown("### 🌍 월별 해외본사 광고 수")
monthly_brands = stat_data.groupby(["조사월", "해외본사"]).size().reset_index(name="건수")
st.dataframe(monthly_brands.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

# ✅ 구글시트 링크
st.markdown("""
🔗 [Google Sheet에서 직접 보기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)
""")
