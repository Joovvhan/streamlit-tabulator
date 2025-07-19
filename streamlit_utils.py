import streamlit as st
import pandas as pd

# ✅ 데이터 리스트 렌더링 함수
def render_data_list(data_list):
    for data in data_list:
        with st.container():
            st.checkbox(
                f"{data['id']} 선택",
                key=f"checkbox_{data['id']}",
                value=st.session_state.get(f"checkbox_{data['id']}", False),
            )
            if data["type"] == "text":
                st.text_area(
                    label=data["label"],
                    value=data["content"],
                    height=100,
                    disabled=True,
                )
            elif data["type"] == "table":
                df = pd.DataFrame(data["content"][1:], columns=data["content"][0])
                for col in df.columns:
                    df[col] = df[col].astype(str)
                st.table(df)
            elif data["type"] == "image":
                st.image(data["content"])