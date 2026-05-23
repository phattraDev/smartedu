from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

# Render provides postgres:// — SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fall back to SQLite if no DATABASE_URL is set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./school.db"

if DATABASE_URL.startswith("http"):
    raise RuntimeError(
        "DATABASE_URL must be a PostgreSQL connection string, not the Supabase API URL. "
        "Use the Supabase Database connection URI, for example: "
        "postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres"
    )

db_url = make_url(DATABASE_URL)
print(f"[DB] Using: {db_url.drivername}://{db_url.host or 'local'}/{db_url.database or ''}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
