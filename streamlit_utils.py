import streamlit as st
import pandas as pd
from io import BytesIO

from data_utils import process_docx_file

def render_upload_section():
    """파일 업로더와 업로드 처리 버튼 UI 및 로직을 렌더링합니다."""
    st.subheader("파일 업로드")
    uploaded_files = st.file_uploader(
        "📂 docx 파일 업로드 (여러 개 가능)",
        accept_multiple_files=True, # 항상 True로 설정하여 uploaded_files가 리스트임을 보장
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
    if st.button("✨ 예시 Docx 파일 및 테이블 로드", key="load_example_button"):
        example_file_path = "./text_sample.docx" # 앱 파일과 같은 디렉토리에 'example.docx'를 넣어두세요.

        try:
            with open(example_file_path, "rb") as f:
                docx_content = f.read()

            processed_text_data = process_docx_file(BytesIO(docx_content))

            st.session_state.data_list = processed_text_data
            st.success(f"🎉 '{example_file_path}' 파일 내용과 예시 데이터가 성공적으로 로드되었습니다.")
            st.session_state.files_processed = True # 예시 파일 로드도 처리된 것으로 간주
        except FileNotFoundError:
            st.error(f"⚠️ 오류: 예시 파일 '{example_file_path}'을(를) 찾을 수 없습니다. 앱 파일과 같은 디렉토리에 있는지 확인해주세요.")
        except Exception as e:
            st.error(f"❌ 예시 파일 처리 중 오류 발생: {e}")

def render_data_list(data_list):
    # 👇 for 루프 바깥에 'with st.container()'를 배치하여 전체 리스트를 감쌉니다.
    with st.container(height=768): # <-- 이제 이 컨테이너가 전체 리스트를 담는 하나의 스크롤 영역이 됩니다.
        for i, data in enumerate(data_list):
            # 각 데이터 항목은 컨테이너 안에 순서대로 배치됩니다.
            st.checkbox(
                f"{data['label']} 선택",
                key=f"checkbox_{data['id']}",
                value=st.session_state.get(f"checkbox_{data['id']}", False),
            )

            if data["type"] == "text":
                # st.text_area(
                #     label=data.get("label", ""),
                #     value=data["content"],
                #     height=100, # 참고: 이 height는 개별 text_area의 높이입니다.
                #     disabled=True,
                # )
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

    # 이 버튼을 클릭하면 선택된 데이터가 표시됩니다.
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