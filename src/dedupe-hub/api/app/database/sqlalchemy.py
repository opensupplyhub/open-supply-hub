from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi_utils.guid_type import setup_guids_postgresql
from ..config import settings

POSTGRES_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
print('POSTGRES_URL', POSTGRES_URL)
engine = create_engine(POSTGRES_URL, echo=True)
setup_guids_postgresql(engine)         
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    return Session(engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()