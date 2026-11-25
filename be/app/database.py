from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.config import settings

# TODO: remove echo=True, implement better logging
engine = create_engine(settings.database_url, pool_pre_ping=True, echo=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
  pass

def get_db() -> Generator[Session, None, None]:
  with SessionLocal() as db:
    yield db
