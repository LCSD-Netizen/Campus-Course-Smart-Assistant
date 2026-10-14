"""登录注册与当前用户接口。"""

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
from fastapi import APIRouter
from backend.core.shared import *

router = APIRouter()

@router.get('/api/health')
def health():
    """处理health相关业务逻辑。"""
    return {'status': 'ok', 'agent_configured': bool(os.getenv('OPENAI_API_KEY'))}


@router.post('/api/auth/register')
def register(body: RegisterBody, db: Session=Depends(get_db)):
    """处理register相关业务逻辑。"""
    if len(body.password) < 8:
        raise HTTPException(400, '密码至少需要 8 位')
    if db.scalar(select(User).where(User.username == body.username)):
        raise HTTPException(409, '用户名已存在')
    user = User(username=body.username, display_name=body.display_name, password_hash=password_hash(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'access_token': token_for(user), 'token_type': 'bearer', 'user': {'id': user.id, 'username': user.username, 'display_name': user.display_name, 'role': user.role}}


@router.post('/api/auth/login')
def login(body: Credentials, db: Session=Depends(get_db)):
    """处理login相关业务逻辑。"""
    user = db.scalar(select(User).where(User.username == body.username))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, '用户名或密码错误')
    return {'access_token': token_for(user), 'token_type': 'bearer', 'user': {'id': user.id, 'username': user.username, 'display_name': user.display_name, 'role': user.role}}


@router.get('/api/auth/me')
def me(user: User=Depends(get_user)):
    """处理me相关业务逻辑。"""
    return {'id': user.id, 'username': user.username, 'display_name': user.display_name, 'role': user.role, 'department': user.department}