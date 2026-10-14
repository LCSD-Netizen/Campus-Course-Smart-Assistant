"""SQLAlchemy 数据库实体。"""

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

class Base(DeclarativeBase):
    '''"""Base 数据模型或请求参数结构。"""'''
    pass


class User(Base):
    '''"""User 数据模型或请求参数结构。"""'''
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(80), default='同学')
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(20), default='student')
    department: Mapped[str] = mapped_column(String(100), default='计算机科学与技术')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Course(Base):
    '''"""Course 数据模型或请求参数结构。"""'''
    __tablename__ = 'courses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    teacher: Mapped[str] = mapped_column(String(80), default='任课教师')
    room: Mapped[str] = mapped_column(String(80), default='待安排')
    weekday: Mapped[int] = mapped_column(Integer, default=1)
    start_time: Mapped[str] = mapped_column(String(8), default='08:00')
    end_time: Mapped[str] = mapped_column(String(8), default='09:40')
    weeks: Mapped[str] = mapped_column(String(80), default='1-16周')
    credits: Mapped[int] = mapped_column(Integer, default=3)
    color: Mapped[str] = mapped_column(String(20), default='blue')


class Enrollment(Base):
    '''"""Enrollment 数据模型或请求参数结构。"""'''
    __tablename__ = 'enrollments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'), index=True)


class Task(Base):
    '''"""Task 数据模型或请求参数结构。"""'''
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    course_id: Mapped[int | None] = mapped_column(ForeignKey('courses.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(40), default='作业')
    due_date: Mapped[date] = mapped_column(Date)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)


class Plan(Base):
    '''"""Plan 数据模型或请求参数结构。"""'''
    __tablename__ = 'study_plans'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    title: Mapped[str] = mapped_column(String(180))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class Document(Base):
    '''"""Document 数据模型或请求参数结构。"""'''
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int | None] = mapped_column(ForeignKey('courses.id'), nullable=True)
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)