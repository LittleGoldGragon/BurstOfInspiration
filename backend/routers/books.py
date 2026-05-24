from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from database import get_db
from models import Book, Excerpt
from schemas import BookCreate, BookResponse

router = APIRouter()


@router.get("/books", response_model=list[BookResponse])
async def get_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Book,
            func.count(Excerpt.id).label("excerpt_count")
        )
        .outerjoin(Excerpt)
        .group_by(Book.id)
        .order_by(Book.created_at.desc())
    )
    rows = result.all()
    return [
        {**book.to_dict(), "excerpt_count": cnt}
        for book, cnt in rows
    ]


@router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(data: BookCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Book).where(Book.title == data.title, Book.author == (data.author or ""))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该书籍（同标题+作者）已存在")
    book = Book(**data.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return {**book.to_dict(), "excerpt_count": 0}


@router.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    await db.delete(book)
    await db.commit()
    return None


@router.get("/books/groups")
async def get_book_groups(book_id: int = None, db: AsyncSession = Depends(get_db)):
    book_query = select(Book).options(
        selectinload(Book.excerpts).selectinload(Excerpt.tags)
    ).order_by(Book.created_at.desc())

    if book_id:
        book_query = book_query.where(Book.id == book_id)

    books_result = await db.execute(book_query)
    books = books_result.scalars().unique().all()

    groups = []
    for book in books:
        excerpts = sorted(
            book.excerpts,
            key=lambda e: e.updated_at or e.created_at or "",
            reverse=True
        )
        groups.append({
            "book": book.to_dict(),
            "excerpts": [e.to_dict() for e in excerpts],
        })

    return groups
