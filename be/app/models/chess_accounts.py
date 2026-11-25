import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class ChessAccount(Base):
  __tablename__ = "chess_accounts"
  __table_args__ = (CheckConstraint("username = lower(username)", name="username_lowercase"),)

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(String, unique=True)
  player_uuid: Mapped[uuid.UUID | None] = mapped_column(unique=True)
  last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
