import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, func , Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base

class Book(Base):
    __tablename__ = 'books'

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default=uuid.uuid4,
        index=True,
        doc='Уникальный идентификатор книги',
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        doc='Название книги',
    )

    author: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
        doc='Автор книги'
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        doc='Год издания книги'
    )

    genre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc='Жанр книги'
    )

    pages: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc='Количество страниц'
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        doc='Доступна ли книга для выдачи'
    )




    '''ОПЦИОНАЛЬНО'''
    isbn: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        doc='ISBN книги(уникальный идентификатор'
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extra: Mapped[str] = mapped_column(
        JSON,
        nullable=True,
        doc='Дополнительные метаданные JSON формата'
    )

    """TIMESTAMPS"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc='Дата и время последнего обновления'
    )


    __table_args__ = (
        #Составной индекс для частых
        Index('idx_books_author_year', 'author', 'year'),
        Index('idx_books_genre_available', 'genre', 'available'),
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.book_id},title='{self.title}')>"

