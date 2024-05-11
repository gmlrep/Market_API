from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = 'user'
    user_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(default='users')
    hashed_password: Mapped[str]
    salt: Mapped[str]
    white_list_ip: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())

    tasks: Mapped[list['Tasks']] = relationship(back_populates='user', uselist=True)


class Tasks(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)
    is_shared: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.user_id'), nullable=False)

    user: Mapped['User'] = relationship(back_populates='tasks')
