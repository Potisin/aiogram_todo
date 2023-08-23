from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    catalogs: Mapped['Catalog'] = relationship('Catalog', back_populates='user',
                                               cascade="all, delete-orphan")


class Catalog(Base):
    __tablename__ = 'catalog'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), default='Без названия')
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('user.tg_id'))
    user: Mapped['User'] = relationship('User', back_populates='catalogs')
    tasks: Mapped['Task'] = relationship('Task', back_populates='catalog',
                                         cascade="all, delete-orphan", uselist=True)


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    deadline: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    catalog_id: Mapped[int] = mapped_column(Integer, ForeignKey('catalog.id', ondelete='CASCADE'))
    catalog: Mapped['Catalog'] = relationship('Catalog', back_populates='tasks', passive_deletes=True)
