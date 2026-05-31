import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Task(Base):

    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column()
    due_date: Mapped[datetime.date] = mapped_column()
    status: Mapped[int] = mapped_column()
    assigned_to_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_assigned_to_id"))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_created_by_id"))

    assigned_to: Mapped["User"] = relationship(foreign_keys=[assigned_to_id])
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])