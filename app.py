import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ✅ 앱 시작 로그
st.write("✅ 앱이 시작되었습니다")

# ✅ Streamlit Cloud용 secrets 방식 인증 (수정 완료)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["google"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ✅ 구글시트 URL과 워크시트 이름
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit")
worksheet = spreadsheet.worksheet("2025")  # 반드시 시트명 '2025'
data = pd.DataFrame(worksheet.get_all_records())

# ✅ 앱 제목
st.title("📊 서울 주요 전광판 광고 현황 필터 앱")

# ✅ 엑셀 열 이름 기준 필터 생성
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

filters[col] = st.multiselect(
    col,
    options := ["전체"] + sorted(data[col].astype(str).unique()),
    default=None
)

filtered_data = data.copy()
for column, selected in filters.items():
    if selected:
        filtered_data = filtered_data[filtered_data[column].astype(str).isin(selected)]

# ✅ 필터 결과 출력
st.markdown("### 🔍 필터 결과")
st.dataframe(filtered_data, use_container_width=True)

# ✅ CSV 다운로드 버튼
st.download_button(
    label="📥 필터 결과 CSV 다운로드",
    data=filtered_data.to_csv(index=False).encode('utf-8-sig'),
    file_name="filtered_billboard_data.csv",
    mime="text/csv"
)

st.markdown("### 📈 월별 광고주별 광고 수")

# 조사월과 업종 필터 반영
selected_months = filters.get("조사월", [])
selected_categories = filters.get("업종", [])

# 원본 데이터 복사
target_data = data.copy()

# 조사월 필터링
if selected_months and "전체" not in selected_months:
    target_data = target_data[target_data["조사월"].astype(str).isin(selected_months)]

# 업종 필터링
if selected_categories and "전체" not in selected_categories:
    target_data = target_data[target_data["업종"].astype(str).isin(selected_categories)]

# 그룹화 및 출력
monthly_advertisers = target_data.groupby(["조사월", "광고주(연락처)"]).size().reset_index(name="건수")
st.dataframe(monthly_advertisers.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)

st.markdown("### 🌍 월별 해외본사 광고 수")

# 같은 필터 사용
filtered_for_brands = data.copy()

if selected_months and "전체" not in selected_months:
    filtered_for_brands = filtered_for_brands[filtered_for_brands["조사월"].astype(str).isin(selected_months)]

if selected_categories and "전체" not in selected_categories:
    filtered_for_brands = filtered_for_brands[filtered_for_brands["업종"].astype(str).isin(selected_categories)]

# 그룹화 및 출력
monthly_brands = filtered_for_brands.groupby(["조사월", "해외본사"]).size().reset_index(name="건수")
st.dataframe(monthly_brands.sort_values(by=["조사월", "건수"], ascending=[True, False]), use_container_width=True)


# ✅ 원본 시트 링크
st.markdown("""🔗 [Google Sheet에서 직접 보기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)""")
