# app/api/deps.py
from typing import Generator
import logging
import sqlalchemy.exc as sa_exc
from fastapi import Depends, HTTPException, status
import time
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db, engine, AsyncSessionLocal
from app.models.user import User

security = HTTPBearer()
logger = logging.getLogger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    try:
        start = time.perf_counter()
        result = await db.execute(select(User).where(User.email == email))
        elapsed = (time.perf_counter() - start) * 1000
        logger.info("DB execute (get_current_user) completed in %.2f ms", elapsed)
    except (RuntimeError, sa_exc.DBAPIError) as e:
        # Connection-level errors: attempt to rollback, dispose pool and retry once
        logger.warning("DB connection error on execute; will dispose pool and retry: %s", e)
        try:
            await db.rollback()
        except Exception:
            pass
        try:
            # dispose closes all pooled connections so new ones are created
            await engine.dispose()
        except Exception:
            logger.exception("Failed to dispose engine after DB error")

        # retry with a fresh session
        new_session = AsyncSessionLocal()
        try:
            start = time.perf_counter()
            result = await new_session.execute(select(User).where(User.email == email))
            elapsed = (time.perf_counter() - start) * 1000
            logger.info("DB execute (get_current_user) retry completed in %.2f ms", elapsed)
        except Exception as e2:
            logger.exception("Retry after disposing pool also failed: %s", e2)
            try:
                await new_session.rollback()
            except Exception:
                pass
            finally:
                await new_session.close()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error. Please try again later."
            )
        finally:
            try:
                await new_session.close()
            except Exception:
                pass
    except Exception as e:
        # Generic DB errors -> return 503 and avoid exposing internals
        logger.exception("Unexpected DB error when fetching current user: %s", e)
        try:
            await db.rollback()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error. Please try again later."
        )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
