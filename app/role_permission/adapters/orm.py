import typing
from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base



RolePermission = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE")),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE")),
)

class Role(Base):
    
    __tablename__ = "roles" 
    name: Mapped[str] = mapped_column(String(255), unique=True)
    permissions: Mapped[typing.List["Permission"]] = relationship(
        secondary="role_permissions",
    )

class Permission(Base):

    __tablename__ = "permissions"
    name: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str] = mapped_column(String(255), unique=True)