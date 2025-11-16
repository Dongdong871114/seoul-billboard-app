import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 앱 시작 확인용 로그
st.write("✅ 앱이 시작되었습니다")

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

#### 🧩 드롭다운(선택목록) 해제 방법

- `위치`, `빌딩&전광판`, `업종` 항목은 **기존 값만 선택할 수 있도록 드롭다운 제한**이 걸려 있습니다.
- 만약 **새로운 전광판 이름**이나 **신규 업종**을 추가하려면:

📌 **방법 1**:  
→ 구글시트 상단 메뉴에서  
`데이터 > 데이터 유효성 > 조건 해제` 또는 `리스트 직접 편집`

📌 **방법 2**:  
→ 새로운 값을 하단 빈 행에 자유롭게 입력한 후, 드롭다운 목록 범위를 확장  
예: `업종` 항목 → 드롭다운 범위를 C2:C1000 등으로 수정

💡 **입력 시 띄어쓰기·오타 주의** (필터링 결과에 직접 영향)

---

#### 📊 통계 기능

선택한 조사월/업종 기준으로 다음 통계가 자동 계산됩니다:

1. **📈 광고주별 광고 건수**
2. **🌍 해외본사별 광고 건수**

→ 필터에 맞게 **광고를 가장 많이 집행한 광고주/본사 순으로 정렬됨**

---

#### 📥 기타 안내

| 기능 | 설명 |
|------|------|
| CSV 다운로드 | 필터 결과는 다운로드 버튼으로 저장 가능 |
| 실시간 반영 | 구글시트에서 수정 즉시 앱에 반영됨 |
| 데이터 추가 | 새로운 전광판 열도 가능, 필요 시 변환 스크립트 제공 |

---

#### 📬 문의 및 운영
- 데이터 담당자: **dongsoo8787@naver.com**
- 앱 제작 및 유지관리: **동아미디어솔루션본부**
""")

# ✅ Streamlit secrets 인증 방식
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["google"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
client = gspread.authorize(creds)

# ✅ 구글시트에서 데이터 로드
spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit"
)
worksheet = spreadsheet.worksheet("DATA")  # 시트명 정확히 'DATA'
data = pd.DataFrame(worksheet.get_all_records())

# 컬럼명 앞뒤 공백 제거 (안전용)
data.columns = data.columns.str.strip()

st.title("🎉서울 주요 전광판 광고주 조사🎉")

###############################################################################
# 🔹 권역 및 전광판 리스트 정의 (강남권 / 강북권)
###############################################################################
gangnam_buildings = [
    "K-POP Live",
    "현대백화점",
    "파르나스 미디어타워",
    "코엑스 미디어타워",
    "휴먼타워",
    "YK빌딩",
    "강남빌딩",
    "청담빌딩",
    "S&S타워",
    "로드블록12",
    "랜드마크타워",
    "마스터빌딩",
    "백송빌딩",
    "벤츠빌딩",
    "신웅타워",
    "썬타워",
    "엠포리아빌딩",
    "유경빌딩",
    "한섬빌딩",
    "BMW",
    "SB빌딩",
    "SGF청담타워",
    "SYH빌딩",
]

gangbuk_buildings = [
    "신세계 스퀘어",
    "코리아나호텔(K-VISION)",
    "KT스퀘어",
    "교원내외빌딩",
    "룩스",
    "한국빌딩(ME)",
    "일민미술관",
    "을지한국빌딩",
    "명동N빌딩(MN)",
]

def classify_region(row: pd.Series) -> str:
    """
    빌딩&전광판 기준으로 강남권 / 강북권 분류
    """
    b = str(row.get("빌딩&전광판", "")).strip()
    if b in gangnam_buildings:
        return "강남권"
    if b in gangbuk_buildings:
        return "강북권"
    return ""

# 🔎 권역별 전광판 기준을 페이지에 명시
st.markdown("### 📍 권역별 전광판 기준")
with st.expander("강남권 / 강북권 전광판 목록 보기", expanded=True):
    st.markdown("#### 🟦 강남권 전광판")
    st.markdown("- " + "\n- ".join(gangnam_buildings))

    st.markdown("#### 🟥 강북권 전광판")
    st.markdown("- " + "\n- ".join(gangbuk_buildings))

###############################################################################
# ✅ 필터 기능
###############################################################################
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

filtered_data = data.copy()
for col, selected in filters.items():
    if selected and "전체" not in selected:
        filtered_data = filtered_data[filtered_data[col].astype(str).isin(selected)]

st.markdown("### 🔍 필터 결과")
st.dataframe(filtered_data, use_container_width=True)

st.download_button(
    label="📥 필터 결과 CSV 다운로드",
    data=filtered_data.to_csv(index=False).encode('utf-8-sig'),
    file_name="filtered_billboard_data.csv",
    mime="text/csv"
)

###############################################################################
# ✅ 기본 통계 기능
###############################################################################
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

monthly_advertisers = (
    stat_data
    .groupby(["조사월", "광고주(연락처)"])
    .size()
    .reset_index(name="건수")
)
st.dataframe(
    monthly_advertisers.sort_values(by=["조사월", "건수"], ascending=[True, False]),
    use_container_width=True
)

st.markdown("### 🌍 월별 해외본사 광고 수")
monthly_brands = (
    stat_data
    .groupby(["조사월", "해외본사"])
    .size()
    .reset_index(name="건수")
)
st.dataframe(
    monthly_brands.sort_values(by=["조사월", "건수"], ascending=[True, False]),
    use_container_width=True
)

###############################################################################
# 🟦 신규 기능 1: K-VISION & KT스퀘어 단독 광고 분석 (룩스 제외 · 공익 제외)
###############################################################################
st.markdown("## 🟦 K-VISION & KT스퀘어 단독 광고 분석 (룩스 제외 · 공익 제외)")
st.write(
    "선택한 조사월 범위에서 **공익 광고를 제외하고**, "
    "**코리아나호텔(K-VISION)**과 **KT스퀘어** 전광판에만 등장하며 "
    "**룩스에는 등장하지 않은 광고주**를 표로 나열합니다. "
    "추가로, 해당 광고주가 과거 **일민미술관**에 광고한 적이 있다면 그 조사월을 표시하고, "
    "해당 광고가 **K-VISION인지 / KT스퀘어인지 / 둘 다인지**도 함께 보여줍니다."
)

multi_months = st.multiselect(
    "분석할 조사월 선택 (복수 선택 가능)",
    month_options,
    default=[],
)

if multi_months:
    base = data.copy()
    subset = base[
        (base["조사월"].astype(str).isin(multi_months)) &
        (base["위치"] == "광화문") &
        (~base["업종"].astype(str).str.contains("공익", na=False))
    ]

    kvkt = subset[subset["빌딩&전광판"].isin(["코리아나호텔(K-VISION)", "KT스퀘어"])]
    lux = subset[subset["빌딩&전광판"] == "룩스"]

    kvkt_adv = kvkt["광고주(연락처)"].astype(str)
    lux_adv = lux["광고주(연락처)"].astype(str).unique()

    # 룩스에 없는 광고주만 필터
    unique_kvkt = kvkt[~kvkt_adv.isin(lux_adv)].copy()

    # 광고주 단위로 기본 정보 집계
    grouped = (
        unique_kvkt
        .groupby("광고주(연락처)")
        .agg({
            "제품&브랜드": "first",
            "해외본사": "first"
        })
        .reset_index()
    )

    # 🔹 (1) 전광판 종류(K-VISION / KT스퀘어 / 둘 다) 계산
    boards_per_adv = (
        unique_kvkt
        .groupby("광고주(연락처)")["빌딩&전광판"]
        .unique()
        .reset_index()
    )

    def label_board(arr):
        s = set(arr)
        has_kv = "코리아나호텔(K-VISION)" in s
        has_kt = "KT스퀘어" in s
        if has_kv and has_kt:
            return "K-VISION & KT스퀘어"
        elif has_kv:
            return "K-VISION"
        elif has_kt:
            return "KT스퀘어"
        return ""

    boards_per_adv["전광판 구분"] = boards_per_adv["빌딩&전광판"].apply(label_board)
    boards_per_adv = boards_per_adv[["광고주(연락처)", "전광판 구분"]]

    # 🔹 (2) 국적 & 일민미술관 광고월 계산
    ilmin_rows = []
    for idx, row in grouped.iterrows():
        adv = str(row["광고주(연락처)"])
        foreign_hq = str(row.get("해외본사", "") or "")
        nationality = "해외" if foreign_hq.strip() != "" else "국내"

        ilmin = base[
            (base["빌딩&전광판"] == "일민미술관") &
            (base["광고주(연락처)"].astype(str) == adv)
        ]
        months_ilmin = sorted(ilmin["조사월"].astype(str).unique())
        ilmin_months_str = ", ".join(months_ilmin) if months_ilmin else ""

        ilmin_rows.append((adv, nationality, ilmin_months_str))

    ilmin_df = pd.DataFrame(ilmin_rows, columns=["광고주(연락처)", "국적", "일민미술관 광고월"])

    # 🔹 (3) 모든 정보 merge
    grouped = grouped.merge(boards_per_adv, on="광고주(연락처)", how="left")
    grouped = grouped.merge(ilmin_df, on="광고주(연락처)", how="left")

    # 컬럼 순서 정리
    grouped = grouped[[
        "광고주(연락처)",
        "제품&브랜드",
        "해외본사",
        "국적",
        "전광판 구분",
        "일민미술관 광고월",
    ]]

    st.dataframe(grouped, use_container_width=True)
else:
    st.info("분석할 조사월을 하나 이상 선택하면 K-VISION & KT스퀘어 단독 광고 목록이 표시됩니다.")

###############################################################################
# 🟥 신규 기능 2: 강남권 vs 강북권 업종/광고주 TOP20 비교 (공익 제외, 월별 필터)
###############################################################################
st.markdown("## 🟥 강남권 vs 강북권 비교 분석 (공익 제외)")

# 🔸 월별 필터 추가 (전체 or 특정 조사월)
region_month = st.selectbox(
    "강남권 vs 강북권 비교에 사용할 조사월 선택",
    ["전체"] + month_options
)

region_df = data.copy()
region_df["권역"] = region_df.apply(classify_region, axis=1)
region_df = region_df[region_df["권역"].isin(["강남권", "강북권"])]
region_df = region_df[region_df["업종"].astype(str).str.strip() != "공익"]

if region_month != "전체":
    region_df = region_df[region_df["조사월"].astype(str) == region_month]

# 🔹 업종 TOP20 (강남/강북)
gn_inds = (
    region_df[region_df["권역"] == "강남권"]["업종"]
    .value_counts()
    .reset_index()
    .head(20)
)
gn_inds.columns = ["강남권 업종", "강남권 건수"]

gb_inds = (
    region_df[region_df["권역"] == "강북권"]["업종"]
    .value_counts()
    .reset_index()
    .head(20)
)
gb_inds.columns = ["강북권 업종", "강북권 건수"]

max_len_ind = max(len(gn_inds), len(gb_inds))
gn_inds = gn_inds.reindex(range(max_len_ind))
gb_inds = gb_inds.reindex(range(max_len_ind))

ind_table = pd.DataFrame({
    "순위": list(range(1, max_len_ind + 1)),
    "강남권 업종": gn_inds["강남권 업종"],
    "강남권 건수": gn_inds["강남권 건수"],
    "강북권 업종": gb_inds["강북권 업종"],
    "강북권 건수": gb_inds["강북권 건수"],
})

if region_month == "전체":
    title_suffix = " (전체 기간 기준)"
else:
    title_suffix = f" ({region_month} 기준)"

st.markdown("### 🔵 업종 TOP20 비교" + title_suffix)
st.dataframe(ind_table, use_container_width=True)

# 🔹 광고주 TOP20 (강남/강북)
gn_adv = (
    region_df[region_df["권역"] == "강남권"]["광고주(연락처)"]
    .value_counts()
    .reset_index()
    .head(20)
)
gn_adv.columns = ["강남권 광고주", "강남권 건수"]

gb_adv = (
    region_df[region_df["권역"] == "강북권"]["광고주(연락처)"]
    .value_counts()
    .reset_index()
    .head(20)
)
gb_adv.columns = ["강북권 광고주", "강북권 건수"]

# 국적 붙이기
gn_nat = []
for adv in gn_adv["강남권 광고주"].dropna():
    sub = region_df[
        (region_df["권역"] == "강남권") &
        (region_df["광고주(연락처)"].astype(str) == str(adv))
    ]
    has_foreign = (
        sub["해외본사"].notna().any()
        and (sub["해외본사"].astype(str).str.strip() != "").any()
    )
    gn_nat.append("해외" if has_foreign else "국내")
gn_adv["강남권 국적"] = gn_nat + [""] * (len(gn_adv) - len(gn_nat))

gb_nat = []
for adv in gb_adv["강북권 광고주"].dropna():
    sub = region_df[
        (region_df["권역"] == "강북권") &
        (region_df["광고주(연락처)"].astype(str) == str(adv))
    ]
    has_foreign = (
        sub["해외본사"].notna().any()
        and (sub["해외본사"].astype(str).str.strip() != "").any()
    )
    gb_nat.append("해외" if has_foreign else "국내")
gb_adv["강북권 국적"] = gb_nat + [""] * (len(gb_adv) - len(gb_nat))

max_len_adv = max(len(gn_adv), len(gb_adv))
gn_adv = gn_adv.reindex(range(max_len_adv))
gb_adv = gb_adv.reindex(range(max_len_adv))

adv_table = pd.DataFrame({
    "순위": list(range(1, max_len_adv + 1)),
    "강남권 광고주": gn_adv["강남권 광고주"],
    "강남권 건수": gn_adv["강남권 건수"],
    "강남권 국적": gn_adv["강남권 국적"],
    "강북권 광고주": gb_adv["강북권 광고주"],
    "강북권 건수": gb_adv["강북권 건수"],
    "강북권 국적": gb_adv["강북권 국적"],
})

st.markdown("### 🔴 광고주 TOP20 비교" + title_suffix)
st.dataframe(adv_table, use_container_width=True)

# ✅ 구글시트 링크
st.markdown("""
🔗 [Google Sheet에서 직접 보기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)
""")
