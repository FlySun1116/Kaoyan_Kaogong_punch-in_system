from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY
from app.database import get_db
from app.models import SystemSetting
from app.routers import admin, auth, data, pages, plans, punches, stats, subjects

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="考研考公学习打卡系统", description="考研/考公学习打卡管理系统")

# Session 中间件（14 天有效期）
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=14 * 24 * 3600,
)

# 认证路由
app.include_router(auth.router)

# API 路由
app.include_router(admin.router)
app.include_router(subjects.router)
app.include_router(plans.router)
app.include_router(punches.router)
app.include_router(stats.router)
app.include_router(data.router)

# 页面路由（放在 API 之后，避免路径冲突）
app.include_router(pages.router)

# 静态资源
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "templates" / "static")),
    name="static",
)

# 用户上传/品牌资源（app/static/）
app.mount(
    "/assets",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="assets",
)


@app.get("/api/settings")
def read_settings(db: Session = Depends(get_db)):
    settings = db.query(SystemSetting).all()
    return {item.key: item.value for item in settings}


@app.on_event("startup")
def on_startup():
    """启动时初始化数据库表与种子"""
    from app.init_db import init
    init()
