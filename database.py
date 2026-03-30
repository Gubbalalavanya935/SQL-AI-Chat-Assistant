from sqlalchemy import create_engine

# 🔐 Update with your actual MySQL credentials
DB_URL = "mysql+pymysql://root:Ammu%408571@localhost:3306/school_db"

engine = create_engine(
    DB_URL,
    echo=False,        # set True only for debugging
    future=True        # modern SQLAlchemy behavior
)