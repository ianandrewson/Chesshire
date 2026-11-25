import uuid
from datetime import datetime

from typing import Any
from sqlalchemy import String, DateTime, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base

class Game(Base):
  __tablename__ = "games"

  chess_uuid: Mapped[uuid.UUID] = mapped_column(primary_key=True)
  pgn: Mapped[str] = mapped_column(Text)
  time_control: Mapped[str] = mapped_column(String)
  time_class: Mapped[str] = mapped_column(String)
  chess_url: Mapped[str] = mapped_column(String)
  eco: Mapped[str | None] = mapped_column(String)
  raw: Mapped[dict[str, Any]] = mapped_column(JSONB)
  end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
  rules: Mapped[str] = mapped_column(String)
  rated: Mapped[bool] = mapped_column(Boolean)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())