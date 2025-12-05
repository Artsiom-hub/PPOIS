# infrastructure/api/book_controller.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .dependencies import get_book_service
from Core_Domains.book_catalog.services import BookCatalogService

router = APIRouter(prefix="/books", tags=["Books"])


class BookSearchDTO(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None


@router.post("/search")
def search_books(dto: BookSearchDTO, svc: BookCatalogService = Depends(get_book_service)):
    results = svc.search(title=dto.title, author=dto.author, genre=dto.genre)
    return [b.title for b in results]
