from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Tag
from schemas import TagCreate, TagResponse

router = APIRouter()


@router.get("/tags", response_model=list[TagResponse])
async def get_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.created_at))
    tags = result.scalars().all()
    return [t.to_dict() for t in tags]


@router.post("/tags", response_model=TagResponse, status_code=201)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tag).where(Tag.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="标签名已存在")
    tag = Tag(**data.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag.to_dict()


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    await db.delete(tag)
    await db.commit()
    return None
