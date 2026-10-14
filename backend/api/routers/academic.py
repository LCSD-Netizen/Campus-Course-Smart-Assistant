"""课表、任务和学习计划接口。"""

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

@router.get('/api/dashboard')
def dashboard(user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理dashboard相关业务逻辑。"""
    courses = db.scalars(select(Course).join(Enrollment).where(Enrollment.user_id == user.id)).all()
    tasks = db.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.due_date)).all()
    plans = db.scalars(select(Plan).where(Plan.user_id == user.id).order_by(Plan.created_at.desc()).limit(5)).all()
    enrolled = [c.id for c in courses]
    docs = db.scalar(select(func.count(Document.id)).where(Document.course_id.is_(None) | Document.course_id.in_(enrolled if enrolled else [-1]))) or 0
    return {'courses': [course_json(c) for c in courses], 'tasks': [task_json(t, db) for t in tasks], 'plans': [{'id': p.id, 'title': p.title, 'content': p.content, 'due_date': p.due_date.isoformat() if p.due_date else None, 'created_at': p.created_at.isoformat()} for p in plans], 'stats': {'courses': len(courses), 'pending_tasks': sum((not t.completed for t in tasks)), 'documents': docs}}


@router.get('/api/schedule')
def schedule(user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理schedule相关业务逻辑。"""
    courses = db.scalars(select(Course).join(Enrollment).where(Enrollment.user_id == user.id).order_by(Course.weekday, Course.start_time)).all()
    return [course_json(c) for c in courses]


@router.get('/api/courses')
def list_courses(user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理list_courses相关业务逻辑。"""
    query = select(Course).order_by(Course.weekday, Course.start_time)
    if user.role != 'admin':
        query = query.join(Enrollment).where(Enrollment.user_id == user.id)
    return [course_json(c) for c in db.scalars(query).all()]


@router.get('/api/tasks')
def list_tasks(user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理list_tasks相关业务逻辑。"""
    tasks = db.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.due_date)).all()
    return [task_json(t, db) for t in tasks]


@router.post('/api/tasks')
def add_task(body: TaskBody, user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理add_task相关业务逻辑。"""
    if body.course_id and (not db.scalar(select(Enrollment).where(Enrollment.user_id == user.id, Enrollment.course_id == body.course_id))):
        raise HTTPException(403, '无权为该课程创建任务')
    row = Task(user_id=user.id, course_id=body.course_id, title=body.title, kind=body.kind, due_date=body.due_date)
    db.add(row)
    db.commit()
    db.refresh(row)
    return task_json(row, db)


@router.patch('/api/tasks/{task_id}/complete')
def complete_task(task_id: int, user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理complete_task相关业务逻辑。"""
    row = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    if not row:
        raise HTTPException(404, '任务不存在')
    row.completed = not row.completed
    db.commit()
    return task_json(row, db)


@router.get('/api/plans')
def list_plans(user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理list_plans相关业务逻辑。"""
    rows = db.scalars(select(Plan).where(Plan.user_id == user.id).order_by(Plan.created_at.desc())).all()
    return [{'id': p.id, 'title': p.title, 'content': p.content, 'due_date': p.due_date.isoformat() if p.due_date else None, 'created_at': p.created_at.isoformat()} for p in rows]


@router.post('/api/plans')
def create_plan(body: PlanBody, user: User=Depends(get_user), db: Session=Depends(get_db)):
    """处理create_plan相关业务逻辑。"""
    row = Plan(user_id=user.id, title=body.title, content=body.content, due_date=body.due_date)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {'id': row.id, 'title': row.title, 'content': row.content, 'due_date': row.due_date.isoformat() if row.due_date else None}