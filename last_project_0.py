from dotenv import load_dotenv
import os
from pathlib import Path
import streamlit as st
from groq import Groq
import PyPDF2

#streamlit run last_project_0.py

# ✅ 환경변수 로드 (.env에 GROQ_API_KEY 저장)
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
key = os.getenv("GROQ_API_KEY")
if not key:
    raise RuntimeError("❌ GROQ_API_KEY not found. Check your .env file.")
client = Groq(api_key=key)

# ✅ Streamlit 기본 설정
st.set_page_config(page_title="AI 학습 퀴즈 생성기", page_icon="🧠", layout="wide")
st.title("AI 학습 퀴즈 생성기")
st.markdown("PDF나 TXT 파일을 업로드하면 AI가 자동으로 퀴즈를 만들어줍니다. (Groq Llama 3.1 기반)")

# ✅ 파일 업로더
uploaded_files = st.file_uploader(
    "📂 PDF 또는 TXT 파일을 업로드하세요",
    accept_multiple_files=True,
    type=["pdf", "txt"]
)

num = st.slider("출제 문항 수", 5, 30, 20)

# ✅ PDF / TXT 읽기 함수
def read_uploaded_files(files):
    text = ""
    for file in files:
        if file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif file.name.endswith(".txt"):
            try:
                text += file.read().decode("utf-8") + "\n"
            except AttributeError:
                text += file.read() + "\n"
    return text.strip()

# ✅ 퀴즈 생성 버튼
if st.button("🧩 퀴즈 생성"):
    if not uploaded_files:
        st.warning("PDF 또는 TXT 파일을 업로드하세요.")
        st.stop()

    # 파일 텍스트 읽기
    content = read_uploaded_files(uploaded_files)

    # 너무 긴 경우 자동 요약
    if len(content) > 6000:
        st.warning("⚠️ 내용이 너무 깁니다. 요약 중입니다...")
        content = content[:6000]

    st.info("✅ 파일에서 텍스트 추출 완료!")

    # 프롬프트 구성
    prompt = f"""
    아래 내용을 기반으로 {num}문항의 객관식 퀴즈를 만들어줘.
    각 문항은 4지선다형이고, 정답과 해설도 포함해줘.
    내용:
    {content}
    """

    st.info("⏳ Groq AI가 퀴즈를 생성 중입니다. 잠시만 기다려주세요...")

    # ✅ Groq API 호출 (무료 Llama 3.1)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "너는 퀴즈를 잘 만드는 교사야."},
            {"role": "user", "content": prompt}
        ]
    )

    st.success("✅ 퀴즈 생성 완료!")
    st.write(response.choices[0].message.content)