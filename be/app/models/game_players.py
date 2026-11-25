import uuid

from app.database import Base

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class GamePlayer(Base):
  __tablename__ = "game_players"
  __table_args__ = (UniqueConstraint("game_uuid", "color"),)

  id: Mapped[int] = mapped_column(primary_key=True)
  rating: Mapped[int] = mapped_column()
  result: Mapped[str] = mapped_column(String)
  username: Mapped[str] = mapped_column(String)
  game_uuid: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.chess_uuid"))
  player_uuid: Mapped[uuid.UUID] = mapped_column(index=True)
  color: Mapped[str] = mapped_column(String)
