import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 앱 시작 확인용 로그
st.write("✅ 앱이 시작되었습니다")

# ✅ Streamlit Cloud secrets 인증 방식
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["google"]
creds_json = json.dumps(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
client = gspread.authorize(creds)

# ✅ 구글시트 불러오기
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit")
worksheet = spreadsheet.worksheet("2025")
data = pd.DataFrame(worksheet.get_all_records())

# ✅ 앱 타이틀
st.title("📊 서울 주요 전광판 광고 현황 필터 앱")

# ✅ 필터 항목 정의
filter_columns = [
    "조사월",
    "위치",
    "빌딩&전광판",
    "업종",
    "제품&브랜드",
    "광고대행사(연락처) ",
    "미디어렛사(연락처)",
    "광고주(연락처)",
    "해외본사"
]

# ✅ 필터 위젯 생성 (전체 옵션 포함)
filters = {}
for col in filter_columns:
    if col in data.columns:
        options = ["전체"] + sorted(data[col].astype(str).unique())
        filters[col] = st.multiselect(col, options, default=["전체"])

# ✅ 필터 적용
filtered_data = data.copy()
for col, selected in filters.items():
    if "전체" not in selected:
        filtered_data = filtered_data[filtered_data[col].astype(str).isin(selected)]

# ✅ 결과 테이블 출력
st.markdown("### 🔍 필터 결과")
st.dataframe(filtered_data, use_container_width=True)

# ✅ CSV 다운로드 버튼
st.download_button(
    label="📅 필터 결과 CSV 다운로드",
    data=filtered_data.to_csv(index=False).encode('utf-8-sig'),
    file_name="filtered_billboard_data.csv",
    mime="text/csv"
)

# ✅ 통계 필터: 조사월, 업종
st.markdown("---")
st.markdown("### 통계 필터")
month_options = ["전체"] + sorted(data["조사월"].astype(str).unique())
selected_month = st.selectbox("해당 조사월", month_options)
sector_options = ["전체"] + sorted(data["업종"].astype(str).unique())
selected_sector = st.selectbox("해당 업종", sector_options)

# ✅ 필터링된 통계 데이터 생성
stat_data = data.copy()
if selected_month != "전체":
    stat_data = stat_data[stat_data["조사월"].astype(str) == selected_month]
if selected_sector != "전체":
    stat_data = stat_data[stat_data["업종"].astype(str) == selected_sector]

# ✅ 광고주별 통계
st.markdown("### 📈 월별 광고주별 광고 수")
ad_stats = stat_data.groupby(["조사월", "광고주(연락처)"]).size().reset_index(name="건수")
st.dataframe(ad_stats.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

# ✅ 해외본사별 통계
st.markdown("### 🌍 월별 해외본사 광고 수")
brand_stats = stat_data.groupby(["조사월", "해외본사"]).size().reset_index(name="건수")
st.dataframe(brand_stats.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

# ✅ 시트 링크
st.markdown("""
🔗 [Google Sheet에서 직접 보기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)
""")
