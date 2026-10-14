"""课程资料查看与上传接口。"""

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
from backend.services.rag import extract_text, split_chunks, vector_add

router = APIRouter()

@router.get('/api/documents')
def list_documents(user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理list_documents相关业务逻辑。"""
    if user.role == 'admin':
        rows = db.scalars(select(Document).order_by(Document.created_at.desc())).all()
        return [{'id': d.id, 'filename': d.filename, 'course_id': d.course_id, 'created_at': d.created_at.isoformat(), 'characters': len(d.content)} for d in rows]
    enrolled = db.scalars(select(Enrollment.course_id).where(Enrollment.user_id == user.id)).all()
    rows = db.scalars(select(Document).where(Document.course_id.is_(None) | Document.course_id.in_(enrolled if enrolled else [-1])).order_by(Document.created_at.desc())).all()
    return [{'id': d.id, 'filename': d.filename, 'course_id': d.course_id, 'created_at': d.created_at.isoformat(), 'characters': len(d.content)} for d in rows]


@router.post('/api/admin/documents')
async def upload_document(file: UploadFile=File(...), course_id: int | None=None, user: User=Depends(admin_only), db: Session=Depends(get_db)):
    """处理upload_document相关业务逻辑。"""
    if Path(file.filename or '').suffix.lower() not in {'.pdf', '.docx', '.pptx', '.txt'}:
        raise HTTPException(400, '不支持的文件格式')
    raw = await file.read()
    if len(raw) > 20 * 1024 * 1024:
        raise HTTPException(413, '单个文件不能超过 20MB')
    if course_id and (not db.get(Course, course_id)):
        raise HTTPException(404, '课程不存在')
    text = await extract_text(file.filename or '资料', raw)
    if not text.strip():
        raise HTTPException(400, '文件中未能提取到文本内容')
    row = Document(filename=Path(file.filename or '资料').name, content=text[:2000000], course_id=course_id, uploaded_by=user.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    await vector_add(row)
    return {'id': row.id, 'filename': row.filename, 'characters': len(row.content), 'chunks': len(split_chunks(row.content))}