import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 앱 시작 확인용 로그
st.write("✅ 앱이 시작되었습니다")

# 구글시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 구글시트 URL 및 시트 이름
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit")
worksheet = spreadsheet.worksheet("2025")  # 반드시 시트명 '2025' 사용
data = pd.DataFrame(worksheet.get_all_records())

# 앱 타이틀
st.title("📊 서울 주요 전광판 광고 현황 필터 앱")

# 엑셀 열 이름 기준 자동 필터 생성
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
        filters[col] = st.multiselect(col, sorted(data[col].astype(str).unique()))

filtered_data = data.copy()
for column, selected in filters.items():
    if selected:
        filtered_data = filtered_data[filtered_data[column].astype(str).isin(selected)]

# 필터 결과 출력
st.markdown("### 🔍 필터 결과")
st.dataframe(filtered_data, use_container_width=True)

# CSV 다운로드 버튼
st.download_button(
    label="📥 필터 결과 CSV 다운로드",
    data=filtered_data.to_csv(index=False).encode('utf-8-sig'),
    file_name="filtered_billboard_data.csv",
    mime="text/csv"
)

# 광고주별 통계
st.markdown("### 📈 월별 광고주별 광고 수")
monthly_advertisers = data.groupby(["조사월", "광고주(연락처)"]).size().reset_index(name="건수")
st.dataframe(monthly_advertisers.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

# 해외본사별 통계
st.markdown("### 🌍 월별 해외본사 광고 수")
monthly_brands = data.groupby(["조사월", "해외본사"]).size().reset_index(name="건수")
st.dataframe(monthly_brands.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

# 원본 시트 링크
st.markdown("""
🔗 [Google Sheet에서 직접 보기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)
""")
