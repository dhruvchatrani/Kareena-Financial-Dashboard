import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The entire database will live in this single, easily transferable file
DB_FILE = "kareena_erp.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(os.getcwd(), DB_FILE)}"

# check_same_thread=False is needed for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
