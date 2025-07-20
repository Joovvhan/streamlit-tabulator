import streamlit as st

st.title("파일 업로드 및 분석 예제")

col1, col2 = st.columns(2)

with col1:
    st.header("문서 파일 업로드")
    doc_files = st.file_uploader(
        "문서 파일을 업로드하세요",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
        key="doc_files"
    )
    doc_analyze = st.button("문서 분석", key="doc_analyze_btn")

    if doc_analyze:
        if not doc_files:
            st.warning("먼저 문서 파일을 업로드해주세요.")
        else:
            st.success(f"문서 {len(doc_files)}개를 분석합니다!")
            for file in doc_files:
                st.write(f"- {file.name}")
                # 분석 로직

with col2:
    st.header("엑셀 파일 업로드")
    excel_files = st.file_uploader(
        "엑셀 파일을 업로드하세요",
        type=["xls", "xlsx"],
        accept_multiple_files=True,
        key="excel_files"
    )
    excel_analyze = st.button("엑셀 분석", key="excel_analyze_btn")

    if excel_analyze:
        if not excel_files:
            st.warning("먼저 엑셀 파일을 업로드해주세요.")
        else:
            st.success(f"엑셀 파일 {len(excel_files)}개를 분석합니다!")
            for file in excel_files:
                st.write(f"- {file.name}")
                # 분석 로직