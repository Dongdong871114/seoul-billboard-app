import streamlit as st
st.write("✅ 앱이 시작되었습니다")

import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# 구글 API 범위 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Streamlit secrets에서 키 가져오기
creds_dict = {
    "type": st.secrets["google"]["type"],
    "project_id": st.secrets["google"]["project_id"],
    "private_key_id": st.secrets["google"]["private_key_id"],
    "private_key": st.secrets["google"]["private_key"],
    "client_email": st.secrets["google"]["client_email"],
    "client_id": st.secrets["google"]["client_id"],
    "auth_uri": st.secrets["google"]["auth_uri"],
    "token_uri": st.secrets["google"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["google"]["client_x509_cert_url"],
    "universe_domain": st.secrets["google"]["universe_domain"]
}

# 구글 API 인증 정보 생성
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
