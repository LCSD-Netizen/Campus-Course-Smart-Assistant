"""集中管理后端配置、数据库连接与认证依赖。"""

from __future__ import annotations
import asyncio
import hashlib
import hmac
import json
import os
import re
import secrets
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, AsyncIterator
import httpx
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, create_engine, delete, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from backend.models.entities import User

ROOT = Path(__file__).resolve().parents[2]


DATA_DIR = ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)


DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/campus.db')

# SQLite 使用项目数据目录；MySQL 使用连接池健康检查。
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL,
        connect_args={'check_same_thread': False},
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


SECRET_KEY = os.getenv('SECRET_KEY', 'development-only-change-this-secret')


ALGORITHM = 'HS256'


bearer = HTTPBearer(auto_error=False)


def password_hash(password: str, salt: str | None=None) -> str:
    '''处理password_hash相关业务逻辑。'''
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 260000).hex()
    return f'{salt}${digest}'


def verify_password(password: str, stored: str) -> bool:
    '''处理verify_password相关业务逻辑。'''
    salt, digest = stored.split('$', 1)
    return hmac.compare_digest(password_hash(password, salt).split('$', 1)[1], digest)


def token_for(user: User) -> str:
    '''处理token_for相关业务逻辑。'''
    return jwt.encode({'sub': str(user.id), 'role': user.role, 'exp': datetime.now(timezone.utc) + timedelta(hours=24)}, SECRET_KEY, algorithm=ALGORITHM)


def get_db():
    '''处理get_db相关业务逻辑。'''
    with SessionLocal() as db:
        yield db


def get_user(credentials: HTTPAuthorizationCredentials | None=Depends(bearer), db: Session=Depends(get_db)) -> User:
    '''处理get_user相关业务逻辑。'''
    if not credentials:
        raise HTTPException(401, '请先登录')
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.get(User, int(payload['sub']))
    except Exception as exc:
        raise HTTPException(401, '登录已过期，请重新登录') from exc
    if not user:
        raise HTTPException(401, '用户不存在')
    return user


def admin_only(user: User=Depends(get_user)) -> User:
    '''处理admin_only相关业务逻辑。'''
    if user.role != 'admin':
        raise HTTPException(403, '需要管理员权限')
    return user


def signed_user_context(user_id: int) -> str:
    '''处理signed_user_context相关业务逻辑。'''
    raw = str(user_id)
    signature = hmac.new(SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return f'{raw}.{signature}'


async def call_mcp_tool(name: str, arguments: dict[str, Any]) -> str | None:
    '''处理call_mcp_tool相关业务逻辑。'''
    url = os.getenv('MCP_URL', 'http://127.0.0.1:8001/mcp')
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client
        async with streamablehttp_client(url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
                return '\n'.join((item.text for item in result.content if hasattr(item, 'text')))
    except Exception:
        return None
