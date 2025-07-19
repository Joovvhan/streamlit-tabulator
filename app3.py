import streamlit as st

from io import BytesIO

from streamlit_utils import render_upload_section
from streamlit_utils import render_data_list, render_selected_data_section

from data_utils import process_xlsx_file

from collections import defaultdict

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

    st.subheader("파일 업로드")
    xlsx_uploaded_files = st.file_uploader(
        "📂 xlsx 파일 업로드",
        # accept_multiple_files=True,
        accept_multiple_files=True,
        type=["xlsx"],
        key="xlsx_uploader" # 고유 키 부여
    )

    if st.button("📤 업로드 파일 처리", key="process_uploaded_xlsx_button"):
        if xlsx_uploaded_files:
            sheet_data = defaultdict(list)

            for f in xlsx_uploaded_files:
                try:
                    extracted = process_xlsx_file(BytesIO(f.getvalue()))  # Dict[sheet_name, List[DataFrame]]

                    for sheet_name, df_list in extracted.items():
                        sheet_data[sheet_name].extend(df_list)

                    st.success(f"'{f.name}' 처리 완료")
                except Exception as e:
                    st.error(f"'{f.name}' 처리 중 오류 발생: {e}")

            # dict 로 저장
            st.session_state.table_data_dict = dict(sheet_data)
            st.session_state.xlsx_files_processed = True
            st.success(f"✅ 총 {len(xlsx_uploaded_files)}개의 파일이 성공적으로 처리되었습니다.")
        else:
            st.warning("업로드된 xlsx 파일이 없습니다.")
            st.session_state.xlsx_files_processed = False

    if st.session_state.get("xlsx_files_processed", False):
        st.subheader("📋 시트별 테이블 미리보기")

        # 1. 모든 시트 모든 테이블(1x1 제외) 정보를 전역 리스트로 수집
        all_table_info = []  # (global_idx, sheet_name, local_idx, label)
        global_idx = 0
        for sheet_name, dfs in st.session_state.table_data_dict.items():
            table_counter = 1
            for local_idx, df in enumerate(dfs):
                if df.shape != (1, 1):
                    label = f"{sheet_name} - 테이블 {table_counter}"
                    all_table_info.append((global_idx, sheet_name, local_idx, label))
                    table_counter += 1
                    global_idx += 1

        # 2. 라디오 버튼 (탭 위, 전역 선택)
        selected_label = st.radio(
            "선택할 테이블을 하나 고르세요",
            [label for _, _, _, label in all_table_info],
            index=0,
            key="radio_all_tables"
        )

        # 3. 선택된 라디오 라벨에 해당하는 전역 인덱스, 시트명, 로컬 인덱스 찾기
        selected_entry = next(e for e in all_table_info if e[3] == selected_label)
        _, selected_sheet_name, selected_local_idx, _ = selected_entry

        st.session_state['current_selected_table'] = {
            "sheet_name": selected_sheet_name,
            "table_index": selected_local_idx
        }

        tabs = st.tabs(list(st.session_state.table_data_dict.keys()))

        for tab, sheet_name in zip(tabs, st.session_state.table_data_dict.keys()):
            with tab:
                dfs = st.session_state.table_data_dict[sheet_name]

                with st.container(height=512):
                    text_counter = 1
                    table_counter = 1

                    for local_idx, df in enumerate(dfs):
                        if df.shape == (1, 1):
                            value = df.iloc[0, 0]
                            st.text(f"📌 텍스트 {text_counter}: {value}")
                            text_counter += 1
                        else:
                            st.divider()  # 구분선

                            label = f"테이블 {table_counter}"
                            if sheet_name == selected_sheet_name and local_idx == selected_local_idx:
                                st.text(f"✅ 📊 {label} (선택됨)")
                            else:
                                st.text(f"📊 {label}")

                            st.dataframe(df, use_container_width=True)
                            table_counter += 1

            # edited_df = st.data_editor(
            #     df,
            #     use_container_width=True,
            #     key=f"editor_{filename}",
            #     num_rows="dynamic",
            # )

            # st.session_state.edited_table_data[filename] = edited_df

            # 입력창 및 버튼 UI
            # m_col1, m_col2, m_col3 = st.columns([2, 1, 1])
            # with m_col1:
            #     column_name = st.text_input(f"열 이름 입력 - {filename}", key=f"input_col_{filename}")
            # with m_col2:
            #     if st.button("➕ 열 추가", key=f"add_col_{filename}"):
            #         if column_name and column_name not in df.columns:
            #             df[column_name] = ""  # 빈 문자열로 새 열 추가
            #             st.success(f"'{column_name}' 열이 추가되었습니다.")
            #             st.rerun()
            #         elif column_name in df.columns:
            #             st.warning(f"'{column_name}' 열이 이미 존재합니다.")
            #         else:
            #             st.warning("열 이름을 입력하세요.")
            # with m_col3:
            #     if st.button("➖ 열 삭제", key=f"del_col_{filename}"):
            #         if column_name and column_name in df.columns:
            #             df.drop(columns=[column_name], inplace=True)
            #             st.success(f"'{column_name}' 열이 삭제되었습니다.")
            #             st.rerun()
            #         elif column_name not in df.columns:
            #             st.warning(f"'{column_name}' 열이 존재하지 않습니다.")
            #         else:
            #             st.warning("열 이름을 입력하세요.")

with col3:
    st.subheader("🖥️ 표 처리")
    st.divider()

    st.subheader("표 편집")
    selection = st.session_state.get('current_selected_table')

    if selection:
        sheet_name = selection["sheet_name"]
        table_index = selection["table_index"]

        dfs = st.session_state.table_data_dict.get(sheet_name)
        if dfs is None:
            st.error(f"'{sheet_name}' 시트를 찾을 수 없습니다.")
        elif table_index >= len(dfs):
            st.error(f"'{sheet_name}' 시트에 테이블 인덱스 {table_index}가 없습니다.")
        else:
            key = f"{sheet_name}_{table_index}"

            df_to_edit = st.session_state.edited_table_data.get(key, dfs[table_index])

            edited_df = st.data_editor(
                df_to_edit,
                use_container_width=True,
                key=f"editor_{key}",
                num_rows="dynamic",
            )

            st.session_state.edited_table_data[key] = edited_df

        m_col1, m_col2, m_col3 = st.columns([1, 1, 1])

        with m_col1:
            if st.button("➕ 열 추가", key=f"add_col_{key}"):
                edited_df[f"{len(edited_df.columns)}"] = None
                st.session_state.edited_table_data[key] = edited_df
                st.success("새 열이 추가되었습니다.")
                st.rerun()

        with m_col2:
            if st.button("➖ 열 삭제", key=f"del_col_{key}"):
                if len(edited_df.columns) > 0:
                    col_to_drop = edited_df.columns[-1]
                    edited_df = edited_df.drop(columns=[col_to_drop])
                    st.session_state.edited_table_data[key] = edited_df
                    st.success(f"열 '{col_to_drop}' 이(가) 삭제되었습니다.")
                    st.rerun()
                else:
                    st.warning("삭제할 열이 없습니다.")

        with m_col3:
            if st.button("↔️ 전치(Transpose)", key=f"transpose_{key}"):
                edited_df = edited_df.transpose()
                # 인덱스 초기화 (선택 사항)
                edited_df.reset_index(drop=True, inplace=True)
                st.session_state.edited_table_data[key] = edited_df
                st.success("테이블이 전치되었습니다.")
                st.rerun()
    else:
        st.info("편집할 테이블을 선택해주세요.")