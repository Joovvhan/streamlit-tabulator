import streamlit as st
import pandas as pd
from docx import Document

from data_utils import process_docx_file
from streamlit_utils import render_data_list

st.title("📄 DOCX 문서 문단 추출 및 시각화")

# ✅ 업로드 처리 플래그 초기화
if "files_processed" not in st.session_state:
    st.session_state.files_processed = False
if "data_list" not in st.session_state:
    st.session_state.data_list = []

# ✅ 파일 업로드 UI
uploaded_files = st.file_uploader(
    "📂 docx 파일 업로드 (여러 개 가능)",
    # accept_multiple_files=True,
    type=["docx"],
)

# ✅ 업로드 처리 버튼
if st.button("📤 업로드 파일 처리"):
    # uploaded_files가 None일 수도 있으니 체크
    if uploaded_files:
        # session_state 초기화
        if "data_list" not in st.session_state:
            st.session_state.data_list = []
        else:
            st.session_state.data_list.clear()

        # 다중 업로드일 경우 (리스트)
        if isinstance(uploaded_files, list):
            for f in uploaded_files:
                st.success(f"{f.name} 처리 완료")
                extracted = process_docx_file(f)
                st.session_state.data_list.extend(extracted)

        # 단일 파일일 경우
        else:
            st.success(f"{uploaded_files.name} 처리 완료")
            extracted = process_docx_file(uploaded_files)
            st.session_state.data_list.extend(extracted)

        st.session_state.files_processed = True

    else:
        st.warning("업로드된 docx 파일이 없습니다.")
        st.session_state.files_processed = False

st.divider()

# ✅ 처리된 데이터 렌더링
if st.session_state.files_processed and st.session_state.data_list:
    render_data_list(st.session_state.data_list)
else:
    st.info("먼저 docx 파일을 업로드하고 처리 버튼을 눌러주세요.")