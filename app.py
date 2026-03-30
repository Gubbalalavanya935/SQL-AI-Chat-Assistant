import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine
from llm_engine import generate_sql
from sql_guard import is_safe_sql
import speech_recognition as sr

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="SQL AI Chat Assistant", layout="wide")
st.title("🧠 SQL AI Chat Assistant")

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox(
    "Choose Operation",
    [
        "AI Chat (Natural Language)",
        "Insert",
        "Update",
        "Delete",
        "Alter Table",
        "Join Queries"
    ]
)

# ---------------- Voice Input ----------------
def voice_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""

# ---------------- Result Explanation ----------------
def explain_result(user_question: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "No records were found."

    return f"The result contains {len(df)} rows and {len(df.columns)} columns."

# ======================================================
# 🔹 1. AI CHAT (SELECT QUERIES)
# ======================================================
if menu == "AI Chat (Natural Language)":

    if "chat" not in st.session_state:
        st.session_state.chat = []

    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.chat_input("Ask about the database...")

    with col2:
        voice_clicked = st.button("🎙")

    if voice_clicked:
        spoken_text = voice_to_text()
        if spoken_text:
            user_input = spoken_text
            st.success(f"You said: {spoken_text}")

    if user_input:
        st.session_state.chat.append(("user", user_input))

        sql_query = generate_sql(user_input)

        if is_safe_sql(sql_query):
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(sql_query))
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())

                explanation = explain_result(user_input, df)
                st.session_state.chat.append(("ai", (df, explanation)))

            except Exception as e:
                st.session_state.chat.append(("ai", str(e)))
        else:
            st.session_state.chat.append(("ai", "❌ Unsafe SQL detected"))

    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            if isinstance(msg, tuple):
                df, explanation = msg
                st.dataframe(df)
                st.caption("🧠 " + explanation)
            else:
                st.write(msg)

# ======================================================
# 🔹 2. INSERT
# ======================================================
elif menu == "Insert":
    st.subheader("➕ Insert Student")

    class_id = st.number_input("Class ID", step=1)
    exam_score = st.number_input("Exam Score", step=0.1)
    productivity = st.number_input("Productivity Score", step=0.1)

    if st.button("Insert"):
        query = """
            INSERT INTO students (class_id, exam_score, productivity_score)
            VALUES (:class_id, :exam_score, :productivity)
        """
        with engine.begin() as conn:
            conn.execute(text(query), {
                "class_id": class_id,
                "exam_score": exam_score,
                "productivity": productivity
            })
        st.success("✅ Student inserted successfully")

# ======================================================
# 🔹 3. UPDATE
# ======================================================
elif menu == "Update":
    st.subheader("✏️ Update Student")

    student_id = st.number_input("Student ID", step=1)
    new_score = st.number_input("New Exam Score", step=0.1)

    if st.button("Update"):
        query = """
            UPDATE students
            SET exam_score = :score
            WHERE student_id = :id
        """
        with engine.begin() as conn:
            conn.execute(text(query), {"score": new_score, "id": student_id})
        st.success("✅ Student updated")

# ======================================================
# 🔹 4. DELETE
# ======================================================
elif menu == "Delete":
    st.subheader("🗑 Delete Student")

    student_id = st.number_input("Student ID to delete", step=1)

    if st.button("Delete"):
        query = "DELETE FROM students WHERE student_id = :id"
        with engine.begin() as conn:
            conn.execute(text(query), {"id": student_id})
        st.success("✅ Student deleted")

# ======================================================
# 🔹 5. ALTER TABLE
# ======================================================
elif menu == "Alter Table":
    st.subheader("🧱 Alter Students Table")

    col_name = st.text_input("New Column Name")
    col_type = st.selectbox("Data Type", ["INT", "DOUBLE", "VARCHAR(100)"])

    if st.button("Add Column"):
        query = f"ALTER TABLE students ADD {col_name} {col_type}"
        with engine.begin() as conn:
            conn.execute(text(query))
        st.success(f"✅ Column `{col_name}` added")

# ======================================================
# 🔹 6. JOIN QUERIES
# ======================================================
elif menu == "Join Queries":
    st.subheader("🔗 Students with Class Names")

    query = """
        SELECT 
            s.student_id,
            s.exam_score,
            c.class_name
        FROM students s
        JOIN classes c
        ON s.class_id = c.id
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    st.dataframe(df)
