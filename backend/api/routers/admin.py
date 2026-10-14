"""管理员用户与选课权限接口。"""

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

@router.get('/api/admin/users')
def admin_users(user: User=Depends(admin_only), db: Session=Depends(get_db)):
    """处理admin_users相关业务逻辑。"""
    rows = db.scalars(select(User).order_by(User.id)).all()
    enrollments = db.scalars(select(Enrollment)).all()
    course_map: dict[int, list[int]] = {}
    for enrollment in enrollments:
        course_map.setdefault(enrollment.user_id, []).append(enrollment.course_id)
    return [{'id': u.id, 'username': u.username, 'display_name': u.display_name, 'role': u.role, 'department': u.department, 'course_ids': course_map.get(u.id, []), 'created_at': u.created_at.isoformat()} for u in rows]


@router.patch('/api/admin/users/{user_id}/role')
def set_user_role(user_id: int, body: UserRoleBody, user: User=Depends(admin_only), db: Session=Depends(get_db)):
    """处理set_user_role相关业务逻辑。"""
    if body.role not in {'student', 'admin'}:
        raise HTTPException(400, '无效角色')
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, '用户不存在')
    target.role = body.role
    db.commit()
    return {'id': target.id, 'role': target.role}


@router.put('/api/admin/users/{user_id}/courses')
def set_user_courses(user_id: int, body: CourseAccessBody, user: User=Depends(admin_only), db: Session=Depends(get_db)):
    """处理set_user_courses相关业务逻辑。"""
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, '用户不存在')
    if target.role == 'admin':
        raise HTTPException(400, '管理员账户不使用学生选课权限')
    ids = list(dict.fromkeys(body.course_ids))
    existing = set(db.scalars(select(Course.id).where(Course.id.in_(ids or [-1]))).all())
    if existing != set(ids):
        raise HTTPException(400, '包含无效课程')
    db.execute(delete(Enrollment).where(Enrollment.user_id == user_id))
    db.add_all([Enrollment(user_id=user_id, course_id=course_id) for course_id in ids])
    db.commit()
    return {'user_id': user_id, 'course_ids': ids}