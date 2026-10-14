"""后端启动时的数据准备任务。"""

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
from backend.core.shared import *
from backend.services.rag import vector_add

async def index_seed_docs():
    """启动时将已存在的课程资料重新写入向量数据库。"""
    if os.getenv('EMBEDDING_API_KEY'):
        with SessionLocal() as db:
            for doc in db.scalars(select(Document)).all():
                await vector_add(doc)
