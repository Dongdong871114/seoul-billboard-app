import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 앱 시작 확인 메시지
st.write("✅ 앱이 시작되었습니다")

# Google Sheets 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 시트 불러오기
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit")
worksheet = spreadsheet.worksheet("2025")

# 시트 데이터를 DataFrame으로 변환
data = pd.DataFrame(worksheet.get_all_records())

st.title("📊 서울 주요 전광판 광고 현황 필터 앱")

# 자동 필터 생성
filters = {
    "조사월": st.multiselect("조사월", sorted(data["조사월"].astype(str).unique())),
    "빌딩&전광판": st.multiselect("광고판명", sorted(data["빌딩&전광판"].unique())),
    "광고주": st.multiselect("광고주", sorted(data["광고주"].unique())),
    "제품명": st.multiselect("제품명", sorted(data["제품명"].unique())),
    "업종": st.multiselect("업종", sorted(data["업종"].unique())),
    "브랜드": st.multiselect("브랜드", sorted(data["브랜드"].unique())),
    "해외본사": st.multiselect("해외본사", sorted(data["해외본사"].unique())),
    "소재지": st.multiselect("소재지", sorted(data["소재지"].unique())),
    "매체사": st.multiselect("매체사", sorted(data["매체사"].unique()))
}

# 필터 적용
filtered_data = data.copy()
for column, selected in filters.items():
    if selected:
        filtered_data = filtered_data[filtered_data[column].astype(str).isin(selected)]

st.markdown("### 📌 필터 결과")
st.dataframe(filtered_data, use_container_width=True)

# CSV 다운로드 기능
csv = filtered_data.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 결과 CSV 다운로드",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)

# 통계 분석
st.markdown("### 📈 월별 광고주별 광고 수")
monthly_advertisers = data.groupby(["조사월", "광고주"]).size().reset_index(name="건수")
st.dataframe(monthly_advertisers.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

st.markdown("### 🌍 월별 글로벌 브랜드 광고 수")
monthly_brands = data.groupby(["조사월", "해외본사"]).size().reset_index(name="건수")
st.dataframe(monthly_brands.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

# 구글시트 바로가기
st.markdown("""
🔗 [Google Sheet에서 직접 보기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)
""")
