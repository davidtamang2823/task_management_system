import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String
from database import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=False)
    verified_at: Mapped[datetime.datetime | None] = mapped_column(default=None)
    verification_token: Mapped[str | None] = mapped_column(default=None)
    token_expires_at: Mapped[datetime.datetime | None] = mapped_column(default=None)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", name="fk_role_id"))
    role: Mapped["Role"] = relationship()
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", name="fk_manager_id"), default=None)
    manager: Mapped["User | None"] = relationship("User", back_populates="subordinates", remote_side="User.id")
    subordinates: Mapped[list["User"]] = relationship("User", back_populates="manager")