import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env file")

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
You are an expert MySQL assistant.

Database name: school_db

Tables and schema:

1) classes
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- class_name (VARCHAR)

2) students
- student_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- screen_time_hours (DOUBLE)
- exercise_minutes (INT)
- caffeine_intake_mg (INT)
- part_time_job (INT)
- upcoming_deadline (INT)
- internet_quality (TEXT)
- mental_health_score (INT)
- focus_index (DOUBLE)
- burnout_level (DOUBLE)
- productivity_score (DOUBLE)
- exam_score (DOUBLE)
- class_id (INT, FOREIGN KEY → classes.id)

Rules:
- Generate ONLY valid MySQL SQL.
- Do NOT explain the query.
- Do NOT include markdown or backticks.
- Allowed queries: SELECT, INSERT, UPDATE, DELETE, ALTER.
- Use JOINs when class information is required.
- Never use DROP DATABASE or DROP TABLE.
- Always include LIMIT 50 for SELECT queries unless specified.
"""

# -----------------------------
# LLM SETUP
# -----------------------------
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

# -----------------------------
# SQL GENERATOR
# -----------------------------
def generate_sql(question: str) -> str:
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return response.content.strip()