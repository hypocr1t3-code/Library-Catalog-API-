from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from ..schemas.book import (
    BookCreate,
    BookUpdate,
    ShowBook,
    BookFilters,
)
from ..schemas.common import PaginatedResponse, PaginationParams
from ...dependencies import BookService

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "/",
    response_model=ShowBook,
    status_code=status.HTTP_201_CREATED,
    summary="Создать книгу",
    description="Создать новую книгу в каталоге с автоматическим обогащением из Open Library",
)
async def create_book(
        book_data: BookCreate,
        service: BookService,
):

    return await service.create_book(book_data)


@router.get(
    "/",
    response_model=PaginatedResponse[ShowBook],
    summary="Получить список книг",
    description="Получить список книг с фильтрацией и пагинацией",
)
async def get_books(
        service: BookService,
        pagination: Annotated[PaginationParams, Depends()],
        title: str | None = Query(None, description="Поиск по названию"),
        author: str | None = Query(None, description="Поиск по автору"),
        genre: str | None = Query(None, description="Фильтр по жанру"),
        year: int | None = Query(None, description="Фильтр по году"),
        available: bool | None = Query(None, description="Фильтр по доступности"),
):

    books, total = await service.search_books(
        title=title,
        author=author,
        genre=genre,
        year=year,
        available=available,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return PaginatedResponse.create(books, total, pagination)


@router.get(
    "/{book_id}",
    response_model=ShowBook,
    summary="Получить книгу",
    description="Получить информацию о конкретной книге по ID",
)
async def get_book(
        book_id: UUID,
        service: BookService,
):
    """
    Получить книгу по ID.

    Returns:
        ShowBook: Полная информация о книге

    Raises:
        404: Книга не найдена
    """
    return await service.get_book(book_id)


@router.patch(
    "/{book_id}",
    response_model=ShowBook,
    summary="Обновить книгу",
    description="Частичное обновление книги (передаются только изменяемые поля)",
)
async def update_book(
        book_id: UUID,
        book_data: BookUpdate,
        service: BookService,
):
    """
    Обновить книгу.

    Передаются только те поля, которые нужно изменить.
    Остальные поля остаются без изменений.

    Returns:
        ShowBook: Обновленная книга

    Raises:
        404: Книга не найдена
        400: Невалидные данные
    """
    return await service.update_book(book_id, book_data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить книгу",
    description="Удалить книгу из каталога",
)
async def delete_book(
        book_id: UUID,
        service: BookServiceDep,
):
    """
    Удалить книгу.

    Raises:
        404: Книга не найдена
    """
    await service.delete_book(book_id)