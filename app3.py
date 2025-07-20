import streamlit as st

from streamlit_utils import render_upload_section
from streamlit_utils import render_data_list, render_selected_data_section
from streamlit_utils import render_xlsx_upload_section, handle_uploaded_xlsx_files
from streamlit_utils import render_xlsx_table_selector, render_selected_xlsx_tables
from streamlit_utils import render_table_editor, render_table_edit_buttons, handle_table_submission


def initialize_session_state():
    st.session_state.setdefault("files_processed", False)
    st.session_state.setdefault("data_list", [])
    st.session_state.setdefault("edited_table_data", {})

st.set_page_config(layout="wide")

initialize_session_state()

st.title("📖 문서 추출")

col1, col2, col3 = st.columns([1, 1, 1]) 

with col1:

    st.subheader("📄 DOCX 문서 추출")
    st.divider()

    render_upload_section()

    st.divider()

    if st.session_state.data_list:
        render_data_list(st.session_state.data_list)
    else:
        st.info("먼저 docx 파일을 업로드하고 처리 버튼을 누르거나, 예시 파일을 로드해주세요.")

    render_selected_data_section()

with col2:
    st.subheader("📊 XLSX 문서 추출")
    st.divider()

    render_xlsx_upload_section()

    if st.button("📤 업로드 파일 처리", key="process_uploaded_xlsx_button"):
        handle_uploaded_xlsx_files()

    if st.session_state.get("xlsx_files_processed", False):
        st.subheader("📋 시트별 테이블 미리보기")
        render_xlsx_table_selector()
        render_selected_xlsx_tables()

with col3:
    st.subheader("🖥️ 표 처리")
    st.divider()

    st.subheader("표 편집")

    sheet_name, table_index, edited_df = render_table_editor()

    if sheet_name and edited_df is not None:
        render_table_edit_buttons(sheet_name, table_index, edited_df)
        handle_table_submission()