from sqlalchemy import ForeignKey, false
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class UserChessAccount(Base):
  __tablename__ = "user_chess_accounts"

  user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
  chess_account_id: Mapped[int] = mapped_column(ForeignKey("chess_accounts.id", ondelete="CASCADE"), primary_key=True)
  is_primary: Mapped[bool] = mapped_column(server_default=false())
