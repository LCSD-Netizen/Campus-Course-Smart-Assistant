"""SSE 对话接口。"""

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
from backend.services.agent import run_agent

router = APIRouter()

@router.post('/api/chat/stream')
async def chat_stream(body: ChatBody, user: User=Depends(get_user)):
    """处理chat_stream相关业务逻辑。"""

    async def stream():
        with SessionLocal() as db:
            conversation_history = [
                item.model_dump()
                for item in body.history
            ]
            async for item in run_agent(
                body.message,
                user,
                db,
                conversation_history,
            ):
                yield item
    return StreamingResponse(stream(), media_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
