from docx import Document

# ✅ docx 파일 처리 함수 (문단 추출)
def process_docx_file(uploaded_file):
    document = Document(uploaded_file)

    chunks = []
    current_chunk = []

    for para in document.paragraphs:
        text = para.text.strip()
        if not text:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
        else:
            current_chunk.append(text)

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    data_list = []
    for i, chunk in enumerate(chunks):
        # 첫 라인으로 레이블 추출
        first_line = chunk.splitlines()[0] if chunk else f"paragraph_{i}"
        data_list.append(
            {
                "id": f"paragraph_{i}",
                "type": "text",
                "label": first_line,
                "content": chunk,
            }
        )
    return data_list