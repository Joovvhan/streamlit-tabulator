from collections import defaultdict

import streamlit as st
import pandas as pd
from io import BytesIO

from data_utils import process_docx_file
from data_utils import process_xlsx_file

def render_upload_section():
    """파일 업로더와 업로드 처리 버튼 UI 및 로직을 렌더링합니다."""
    st.subheader("파일 업로드")
    uploaded_files = st.file_uploader(
        "📂 docx 파일 업로드",
        accept_multiple_files=True,
        type=["docx"],
        key="docx_uploader" # 고유 키 부여
    )

    if st.button("📤 업로드 파일 처리", key="process_uploaded_button"):
        if uploaded_files:
            # 기존 data_list를 새 업로드 파일로 덮어씁니다.
            st.session_state.data_list = []
            
            # uploaded_files는 accept_multiple_files=True 덕분에 항상 리스트입니다.
            for f in uploaded_files:
                try:
                    # process_docx_file은 BytesIO 객체를 받도록 구현되어야 합니다.
                    extracted = process_docx_file(BytesIO(f.getvalue()))
                    st.session_state.data_list.extend(extracted)
                    st.success(f"'{f.name}' 처리 완료")
                except Exception as e:
                    st.error(f"'{f.name}' 처리 중 오류 발생: {e}")

            st.session_state.files_processed = True
            st.success(f"✅ 총 {len(uploaded_files)}개의 파일이 성공적으로 처리되었습니다.")
        else:
            st.warning("업로드된 docx 파일이 없습니다.")
            st.session_state.files_processed = False

    # --- 예시 파일 로드 버튼 (선택 사항) ---
    # 이 버튼을 클릭하면 미리 정의된 예시 데이터를 로드합니다.
    # if st.button("✨ 예시 Docx 파일 및 테이블 로드", key="load_example_button"):
    #     example_file_path = "./text_sample.docx" # 앱 파일과 같은 디렉토리에 'example.docx'를 넣어두세요.

    #     try:
    #         with open(example_file_path, "rb") as f:
    #             docx_content = f.read()

    #         processed_text_data = process_docx_file(BytesIO(docx_content))

    #         st.session_state.data_list = processed_text_data
    #         st.success(f"🎉 '{example_file_path}' 파일 내용과 예시 데이터가 성공적으로 로드되었습니다.")
    #         st.session_state.files_processed = True # 예시 파일 로드도 처리된 것으로 간주
    #     except FileNotFoundError:
    #         st.error(f"⚠️ 오류: 예시 파일 '{example_file_path}'을(를) 찾을 수 없습니다. 앱 파일과 같은 디렉토리에 있는지 확인해주세요.")
    #     except Exception as e:
    #         st.error(f"❌ 예시 파일 처리 중 오류 발생: {e}")

def render_data_list(data_list):
    with st.container(height=768): # <-- 이제 이 컨테이너가 전체 리스트를 담는 하나의 스크롤 영역이 됩니다.
        for i, data in enumerate(data_list):
            st.checkbox(
                f"{data['label']} 선택",
                key=f"checkbox_{data['id']}",
                value=st.session_state.get(f"checkbox_{data['id']}", False),
            )

            if data["type"] == "text":
                st.text(
                    data["content"] # st.text는 value 매개변수 대신 직접 문자열을 받습니다.
                )
            elif data["type"] == "table":
                df = pd.DataFrame(data["content"][1:], columns=data["content"][0])
                for col in df.columns:
                    df[col] = df[col].astype(str)
                st.table(df)
            elif data["type"] == "image":
                st.image(data["content"])

            st.divider()

def render_selected_data_section():
    
    st.markdown("---") # 섹션 구분선
    st.subheader("선택된 데이터 보기")

    if st.button("✅ **선택된 데이터만 보기**", key="show_selected_data_button"):

        with st.container(height=256):
            selected_data_to_display = []
            # session_state에 data_list가 있고 비어있지 않은지 확인
            if "data_list" in st.session_state and st.session_state.data_list:
                for data_item in st.session_state.data_list:
                    checkbox_key = f"checkbox_{data_item['id']}"
                    # 해당 체크박스가 선택되었는지 확인 (기본값 False)
                    if st.session_state.get(checkbox_key, False):
                        selected_data_to_display.append(data_item)

            if selected_data_to_display:
                for i, selected_item in enumerate(selected_data_to_display):
                    if selected_item['type'] == 'text':
                        st.text(
                            selected_item["content"]
                        )
                    elif selected_item['type'] == 'table':
                        df_selected = pd.DataFrame(selected_item["content"][1:], columns=selected_item["content"][0])
                        st.dataframe(
                            df_selected,
                            use_container_width=True,
                            height=150,
                            key=f"selected_view_table_{selected_item['id']}" # 고유 키
                        )
                    elif selected_item['type'] == 'image':
                        st.image(selected_item['content'], caption=selected_item.get('label', '선택된 이미지'))
                    st.markdown("---") # 각 항목 사이에 구분선
            else:
                st.info("선택된 데이터가 없습니다.")
    else:
        st.info("선택된 데이터를 보려면 버튼을 클릭하세요.")

def render_xlsx_upload_section():
    st.subheader("파일 업로드")
    # st.divider()
    st.session_state.xlsx_uploaded_files = st.file_uploader(
        "📂 xlsx 파일 업로드",
        accept_multiple_files=True,
        type=["xlsx"],
        key="xlsx_uploader"
    )

def handle_uploaded_xlsx_files():
    uploaded_files = st.session_state.get("xlsx_uploaded_files", None)
    if not uploaded_files:
        st.warning("업로드된 xlsx 파일이 없습니다.")
        st.session_state.xlsx_files_processed = False
        return

    sheet_data = defaultdict(list)
    for f in uploaded_files:
        try:
            extracted = process_xlsx_file(BytesIO(f.getvalue()))
            for sheet_name, df_list in extracted.items():
                sheet_data[sheet_name].extend(df_list)
            st.success(f"'{f.name}' 처리 완료")
        except Exception as e:
            st.error(f"'{f.name}' 처리 중 오류 발생: {e}")

    st.session_state.table_data_dict = dict(sheet_data)
    st.session_state.xlsx_files_processed = True
    st.success(f"✅ 총 {len(uploaded_files)}개의 파일이 성공적으로 처리되었습니다.")

def render_xlsx_table_selector():
    all_table_info = []
    global_idx = 0
    for sheet_name, dfs in st.session_state.table_data_dict.items():
        table_counter = 1
        for local_idx, df in enumerate(dfs):
            if df.shape != (1, 1):
                label = f"{sheet_name} - 테이블 {table_counter}"
                all_table_info.append((global_idx, sheet_name, local_idx, label))
                table_counter += 1
                global_idx += 1

    selected_label = st.radio(
        "선택할 테이블을 하나 고르세요",
        [label for _, _, _, label in all_table_info],
        index=0,
        key="radio_all_tables"
    )
    selected_entry = next(e for e in all_table_info if e[3] == selected_label)
    _, sheet_name, local_idx, _ = selected_entry

    st.session_state['current_selected_table'] = {
        "sheet_name": sheet_name,
        "table_index": local_idx
    }

def render_selected_xlsx_tables():
    tabs = st.tabs(list(st.session_state.table_data_dict.keys()))
    selected = st.session_state.get('current_selected_table', {})

    for tab, sheet_name in zip(tabs, st.session_state.table_data_dict.keys()):
        with tab:
            dfs = st.session_state.table_data_dict[sheet_name]
            with st.container(height=512):
                text_counter = 1
                table_counter = 1
                for idx, df in enumerate(dfs):
                    if df.shape == (1, 1):
                        st.text(f"📌 텍스트 {text_counter}: {df.iloc[0, 0]}")
                        text_counter += 1
                    else:
                        st.divider()
                        label = f"테이블 {table_counter}"
                        is_selected = (sheet_name == selected.get("sheet_name") and idx == selected.get("table_index"))
                        st.text(f"{'✅ ' if is_selected else ''}📊 {label}{' (선택됨)' if is_selected else ''}")
                        for col in df.select_dtypes(include='object').columns:
                            df[col] = df[col].astype(str)
                        st.dataframe(df, use_container_width=True)
                        table_counter += 1

def render_table_editor():
    selection = st.session_state.get('current_selected_table')

    if not selection:
        st.info("편집할 테이블을 선택해주세요.")
        return None, None, None  # 이후 버튼 함수에서 활용

    sheet_name = selection["sheet_name"]
    table_index = selection["table_index"]

    dfs = st.session_state.table_data_dict.get(sheet_name)
    if dfs is None:
        st.error(f"'{sheet_name}' 시트를 찾을 수 없습니다.")
        return None, None, None

    if table_index >= len(dfs):
        st.error(f"'{sheet_name}' 시트에 테이블 인덱스 {table_index}가 없습니다.")
        return None, None, None

    key = f"{sheet_name}_{table_index}"
    df_to_edit = st.session_state.edited_table_data.get(key, dfs[table_index]).copy()

    for col in df_to_edit.select_dtypes(include='object').columns:
        df_to_edit[col] = df_to_edit[col].astype(str)

    edited_df = st.data_editor(
        df_to_edit,
        use_container_width=True,
        key=f"editor_{key}",
        num_rows="dynamic",
    )

    for col in edited_df.select_dtypes(include='object').columns:
        edited_df[col] = edited_df[col].astype(str)

    prev_df = st.session_state.edited_table_data.get(key)

    if prev_df is None or not edited_df.equals(prev_df):
        st.session_state.edited_table_data[key] = edited_df
        st.rerun()

    return sheet_name, table_index, edited_df

def render_table_edit_buttons(sheet_name, table_index, edited_df):
    key = f"{sheet_name}_{table_index}"
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
        if st.button("↔️ 전치", key=f"transpose_{key}"):
            edited_df = edited_df.transpose()
            edited_df.reset_index(drop=True, inplace=True)
            st.session_state.edited_table_data[key] = edited_df
            st.success("테이블이 전치되었습니다.")
            st.rerun()

def handle_table_submission():
    if st.button("🧮 표 채우기", key="submission"):
        selected_data_to_print = []

        if st.session_state.get("data_list"):
            for data_item in st.session_state.data_list:
                checkbox_key = f"checkbox_{data_item['id']}"
                if st.session_state.get(checkbox_key, False):
                    selected_data_to_print.append(data_item.get("content", ""))

        print('\n'.join(selected_data_to_print))  # 텍스트 출력 (또는 다른 처리 로직)
        st.success("선택된 데이터를 바탕으로 표를 채웠습니다.")
        st.rerun()