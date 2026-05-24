import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional

from database import get_db, IS_SQLITE
from models import Book, Excerpt, Tag, ExcerptTag
from schemas import ExcerptCreate, ExcerptUpdate, ExcerptResponse

router = APIRouter()


async def _update_excerpt_tags(db: AsyncSession, excerpt_id: int, tag_ids: list[int]):
    from sqlalchemy import delete
    await db.execute(delete(ExcerptTag).where(ExcerptTag.excerpt_id == excerpt_id))
    if tag_ids:
        for tid in tag_ids:
            db.add(ExcerptTag(excerpt_id=excerpt_id, tag_id=tid))
    await db.flush()


def _search_condition(keyword: str):
    """Return WHERE clause for keyword search, adapted to DB type."""
    kw = keyword.strip()
    if IS_SQLITE:
        pattern = f"%{kw}%"
        return or_(
            Excerpt.content.like(pattern),
            Excerpt.insights.like(pattern),
        )
    else:
        return func.match(Excerpt.content, Excerpt.insights).against(kw)


@router.post("/excerpts", response_model=ExcerptResponse, status_code=201)
async def create_excerpt(data: ExcerptCreate, db: AsyncSession = Depends(get_db)):
    book_result = await db.execute(select(Book).where(Book.id == data.book_id))
    if not book_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="书籍不存在")

    excerpt = Excerpt(
        book_id=data.book_id,
        content=data.content or "",
        insights=data.insights or "",
        links=data.links or [],
        images=data.images or [],
    )
    db.add(excerpt)
    await db.flush()

    await _update_excerpt_tags(db, excerpt.id, data.tag_ids or [])
    await db.commit()
    await db.refresh(excerpt)

    result = await db.execute(
        select(Excerpt)
        .options(selectinload(Excerpt.book), selectinload(Excerpt.tags))
        .where(Excerpt.id == excerpt.id)
    )
    return result.scalar_one().to_dict()


@router.get("/excerpts")
async def get_excerpts(
    keyword: Optional[str] = None,
    tag_ids: Optional[str] = None,
    book_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
):
    tag_id_list = [int(x) for x in tag_ids.split(",") if x.strip()] if tag_ids else []

    # Build query
    query = (
        select(Excerpt)
        .options(selectinload(Excerpt.book), selectinload(Excerpt.tags))
    )

    if keyword:
        query = query.where(_search_condition(keyword))

    if book_id:
        query = query.where(Excerpt.book_id == book_id)

    if tag_id_list:
        subq = (
            select(ExcerptTag.excerpt_id)
            .where(ExcerptTag.tag_id.in_(tag_id_list))
            .group_by(ExcerptTag.excerpt_id)
            .having(func.count(ExcerptTag.tag_id) == len(tag_id_list))
        )
        query = query.where(Excerpt.id.in_(subq))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply ordering + pagination
    offset = (page - 1) * page_size
    query = query.order_by(Excerpt.updated_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    excerpts = result.scalars().unique().all()

    return {
        "items": [e.to_dict() for e in excerpts],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/excerpts/{excerpt_id}", response_model=ExcerptResponse)
async def get_excerpt(excerpt_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Excerpt)
        .options(selectinload(Excerpt.book), selectinload(Excerpt.tags))
        .where(Excerpt.id == excerpt_id)
    )
    excerpt = result.scalar_one_or_none()
    if not excerpt:
        raise HTTPException(status_code=404, detail="摘抄不存在")
    return excerpt.to_dict()


@router.put("/excerpts/{excerpt_id}", response_model=ExcerptResponse)
async def update_excerpt(excerpt_id: int, data: ExcerptUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Excerpt)
        .options(selectinload(Excerpt.book), selectinload(Excerpt.tags))
        .where(Excerpt.id == excerpt_id)
    )
    excerpt = result.scalar_one_or_none()
    if not excerpt:
        raise HTTPException(status_code=404, detail="摘抄不存在")

    updates = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for key, val in updates.items():
        setattr(excerpt, key, val)

    if data.tag_ids is not None:
        await _update_excerpt_tags(db, excerpt.id, data.tag_ids)

    await db.commit()
    await db.refresh(excerpt)

    result = await db.execute(
        select(Excerpt)
        .options(selectinload(Excerpt.book), selectinload(Excerpt.tags))
        .where(Excerpt.id == excerpt_id)
    )
    return result.scalar_one().to_dict()


@router.delete("/excerpts/{excerpt_id}", status_code=204)
async def delete_excerpt(excerpt_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Excerpt).where(Excerpt.id == excerpt_id))
    excerpt = result.scalar_one_or_none()
    if not excerpt:
        raise HTTPException(status_code=404, detail="摘抄不存在")
    await db.delete(excerpt)
    await db.commit()
    return None


@router.post("/excerpts/upload")
async def upload_image(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="仅支持 JPEG/PNG/GIF/WebP 图片")

    ext = os.path.splitext(file.filename or ".png")[1] or ".png"
    filename = uuid.uuid4().hex + ext

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {"url": f"/static/{filename}", "filename": filename}
