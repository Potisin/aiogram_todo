from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    task_lists: Mapped['TaskList'] = relationship('TaskList', back_populates='user',
                                                  cascade="save-update, delete, delete-orphan")


class TaskList(Base):
    __tablename__ = 'task_list'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), default='Без названия')
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('user.tg_id'))
    user: Mapped['User'] = relationship('User', back_populates='task_lists')
    tasks: Mapped['Task'] = relationship('Task', back_populates='task_lists',
                                         cascade="save-update, delete, delete-orphan")


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column()
    deadline: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    task_list_id: Mapped[int] = mapped_column(ForeignKey('task_list.id'))
    task_lists: Mapped['TaskList'] = relationship('TaskList', back_populates='tasks')
