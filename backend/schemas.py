from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- Book ---
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: Optional[str] = ""
    cover: Optional[str] = ""


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    cover: str
    created_at: Optional[str] = None
    excerpt_count: Optional[int] = None

    model_config = {"from_attributes": True}


# --- Tag ---
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = "#409EFF"


class TagResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


# --- Excerpt ---
class ExcerptCreate(BaseModel):
    book_id: int
    content: Optional[str] = ""
    insights: Optional[str] = ""
    links: Optional[List[str]] = []
    images: Optional[List[str]] = []
    tag_ids: Optional[List[int]] = []


class ExcerptUpdate(BaseModel):
    book_id: Optional[int] = None
    content: Optional[str] = None
    insights: Optional[str] = None
    links: Optional[List[str]] = None
    images: Optional[List[str]] = None
    tag_ids: Optional[List[int]] = None


class ExcerptResponse(BaseModel):
    id: int
    book_id: int
    content: str
    insights: str
    links: List[str]
    images: List[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    book: Optional[BookResponse] = None
    tags: List[TagResponse] = []

    model_config = {"from_attributes": True}


# --- Pagination ---
class PaginatedExcerpts(BaseModel):
    items: List[ExcerptResponse]
    total: int
    page: int
    page_size: int


# --- BookGroup ---
class BookGroupResponse(BaseModel):
    book: BookResponse
    excerpts: List[ExcerptResponse]
