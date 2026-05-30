"""认证路由：登录、注册、登出"""
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.database import get_db
from app.dependencies import get_current_user
from app.services.auth_service import authenticate, register

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    exam_type: str = "考研"
    target_exam_date: str | None = None


@router.get("/login")
def login_page(request: Request):
    """登录页面"""
    # 已登录则跳首页
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "login.html")


@router.get("/register")
def register_page(request: Request):
    """注册页面"""
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "register.html")


@router.get("/logout")
def logout(request: Request):
    """登出"""
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


@router.post("/api/auth/login")
def api_login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    """API 登录"""
    user = authenticate(db, data.username, data.password)
    request.session["user_id"] = user.id
    return {"ok": True, "username": user.username, "role": user.role}


@router.post("/api/auth/register")
def api_register(
    request: Request,
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """API 注册并自动登录"""
    user = register(db, data.username, data.password, data.exam_type, data.target_exam_date)
    request.session["user_id"] = user.id
    return {"ok": True, "username": user.username, "role": user.role}


@router.get("/api/auth/me")
def api_me(user=Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "exam_type": user.exam_type,
        "target_exam_date": user.target_exam_date,
    }
