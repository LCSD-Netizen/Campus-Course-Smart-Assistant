"""API 请求体的数据校验结构。"""

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
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, create_engine, delete, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

class Credentials(BaseModel):
    '''"""Credentials 数据模型或请求参数结构。"""'''
    username: str
    password: str


class RegisterBody(Credentials):
    '''"""RegisterBody 数据模型或请求参数结构。"""'''
    display_name: str = '同学'


class ChatHistoryMessage(BaseModel):
    """仅允许把普通用户消息和助手最终回复作为上下文传入。"""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatBody(BaseModel):
    """课程问答请求，附带短期会话中的有限历史消息。"""

    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=12)


class PlanBody(BaseModel):
    '''"""PlanBody 数据模型或请求参数结构。"""'''
    title: str
    content: str
    due_date: date | None = None


class TaskBody(BaseModel):
    '''"""TaskBody 数据模型或请求参数结构。"""'''
    title: str
    kind: str = '作业'
    due_date: date
    course_id: int | None = None


class UserRoleBody(BaseModel):
    '''"""UserRoleBody 数据模型或请求参数结构。"""'''
    role: str


class CourseAccessBody(BaseModel):
    '''"""CourseAccessBody 数据模型或请求参数结构。"""'''
    course_ids: list[int]
