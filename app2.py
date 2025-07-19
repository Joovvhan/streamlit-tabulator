import streamlit as st

from streamlit_utils import render_upload_section
from streamlit_utils import render_data_list, render_selected_data_section

def initialize_session_state():
    """앱에 필요한 모든 session_state 변수를 초기화합니다."""
    if "files_processed" not in st.session_state:
        st.session_state.files_processed = False
    if "data_list" not in st.session_state:
        st.session_state.data_list = []

initialize_session_state()

st.title("📄 DOCX 문서 문단 추출 및 시각화")

st.divider()

render_upload_section()

st.divider()

if st.session_state.data_list: # data_list가 비어있지 않으면 렌더링
    render_data_list(st.session_state.data_list)
else:
    st.info("먼저 docx 파일을 업로드하고 처리 버튼을 누르거나, 예시 파일을 로드해주세요.")

render_selected_data_section()
