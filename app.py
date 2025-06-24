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

with st.expander("📘 설명서 보기"):
    st.markdown("""
### 🧾 서울 전광판 광고 필터 앱 사용 설명서

#### 🟦 앱 개요
- 이 앱은 **서울 주요 전광판 광고 현황을 조사월, 업종, 광고주 등으로 필터링하고 통계로 분석하는 도구**입니다.
- 팀원들이 **공통 포맷에 맞게 데이터를 입력하고 공유**할 수 있도록 제작되었습니다.

#### 🟩 사용 대상 구글시트
- 반드시 구글시트의 **`DATA` 시트**에만 입력해야 앱에서 인식됩니다.  
👉 [📄 원본 시트 바로가기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)

---

#### 🟨 필터 가능 항목 (앱 좌측)
- `조사월` (예: 202506 형식)
- `위치`, `빌딩&전광판`, `업종`: ✅ **드롭다운으로만 선택**
- `제품&브랜드`, `광고대행사`, `미디어렙사`, `광고주(연락처)`, `해외본사`: 자유입력

---

#### 🟥 입력 시 주의사항

✅ **광고주 이름의 정확한 통일성 유지가 핵심**입니다.  
필터가 작동하려면 **기존에 쓰인 광고주명과 정확히 일치**해야 하며,  
띄어쓰기·철자·괄호 차이로도 필터링이 되지 않을 수 있습니다.

| ❌ 잘못된 입력     | ✅ 올바른 입력   |
|------------------|----------------|
| 샤넬 코리아       | 샤넬코리아       |
| 구찌 KOREA       | 구찌코리아       |
| 디올(주)          | 디올코리아       |
| 쿠팡 주식회사     | 쿠팡            |

👉 **광고주명은 기존 입력값을 복사해서 붙여넣는 방식 권장**

---

#### 📊 통계 기능

선택한 조사월/업종 기준으로 다음 통계가 자동 계산됩니다:

1. **📈 광고주별 광고 건수**
2. **🌍 해외본사별 광고 건수**

→ 필터에 맞게 **광고를 가장 많이 집행한 광고주/본사 순으로 정렬됨**

---

#### 🧩 기타 안내

| 기능 | 설명 |
|------|------|
| CSV 다운로드 | 필터 결과는 다운로드 버튼으로 저장 가능 |
| 실시간 반영 | 구글시트에서 수정 즉시 앱에 반영됨 |
| 데이터 추가 | 새로운 전광판 열도 가능, 필요 시 변환 스크립트 사용 |

---

#### 📬 문의 및 운영
""")
