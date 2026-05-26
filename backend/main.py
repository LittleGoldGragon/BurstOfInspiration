import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./")
upload_path = os.path.abspath(os.path.join(UPLOAD_DIR, "uploads"))
os.makedirs(upload_path, exist_ok=True)


async def init_db():
    from models import Base
    from database import engine, IS_SQLITE
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if IS_SQLITE:
        from sqlalchemy import select, text
        from models import Tag
        from database import async_session
        async with async_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM tags"))
            count = result.scalar()
            if count == 0:
                default_tags = [
                    ("哲学", "#57534e"),
                    ("心理学", "#78716c"),
                    ("文学", "#a67c52"),
                    ("金句", "#44403c"),
                    ("方法论", "#64748b"),
                    ("待整理", "#a8a29e"),
                ]
                for name, color in default_tags:
                    session.add(Tag(name=name, color=color))
                await session.commit()


app = FastAPI(title="读书摘抄检索系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import books, excerpts, tags

app.include_router(books.router, prefix="/api", tags=["books"])
app.include_router(excerpts.router, prefix="/api", tags=["excerpts"])
app.include_router(tags.router, prefix="/api", tags=["tags"])

app.mount("/static", StaticFiles(directory=upload_path), name="static")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
