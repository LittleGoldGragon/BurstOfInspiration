from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    JSON
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), default="")
    cover = Column(String(500), default="")
    created_at = Column(DateTime, server_default=func.current_timestamp())

    excerpts = relationship("Excerpt", back_populates="book", cascade="all, delete-orphan")

    def to_dict(self, excerpt_count=None):
        d = {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "cover": self.cover,
            "created_at": str(self.created_at) if self.created_at else None,
        }
        if excerpt_count is not None:
            d["excerpt_count"] = excerpt_count
        return d


class Excerpt(Base):
    __tablename__ = "excerpts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text)
    insights = Column(Text)
    links = Column(JSON, default=list)
    images = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    book = relationship("Book", back_populates="excerpts")
    tags = relationship("Tag", secondary="excerpt_tags", back_populates="excerpts", lazy="selectin")

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "content": self.content or "",
            "insights": self.insights or "",
            "links": self.links or [],
            "images": self.images or [],
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
            "book": self.book.to_dict() if self.book else None,
            "tags": [t.to_dict() for t in self.tags] if self.tags else [],
        }


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), default="#409EFF")
    created_at = Column(DateTime, server_default=func.current_timestamp())

    excerpts = relationship("Excerpt", secondary="excerpt_tags", back_populates="tags")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_at": str(self.created_at) if self.created_at else None,
        }


class ExcerptTag(Base):
    __tablename__ = "excerpt_tags"

    excerpt_id = Column(Integer, ForeignKey("excerpts.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
