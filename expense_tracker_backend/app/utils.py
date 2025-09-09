import datetime
from functools import wraps
from typing import Any, Dict

import jwt
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import settings
from .models import Base, User


# SQLAlchemy engine and session factory
engine = create_engine(settings.DB_URL, pool_pre_ping=True, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


def init_db() -> None:
    """Create all database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


# PUBLIC_INTERFACE
def get_db():
    """Provide a SQLAlchemy scoped session. Remember to close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PUBLIC_INTERFACE
def create_access_token(identity: str) -> str:
    """Create a signed JWT token with subject as the given identity (email)."""
    exp_minutes = settings.JWT_ACCESS_TOKEN_EXPIRES_MIN
    payload = {
        "sub": identity,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes),
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


# PUBLIC_INTERFACE
def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token, returning the payload or raising jwt exceptions."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])


# PUBLIC_INTERFACE
def jwt_required(fn):
    """Decorator that enforces presence of a valid Bearer JWT token. Injects current_user on flask.g."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid Authorization header"}, 401
        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
            email = payload.get("sub")
            if not email:
                return {"message": "Invalid token subject"}, 401
        except jwt.ExpiredSignatureError:
            return {"message": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"message": "Invalid token"}, 401

        # Attach user to request context
        from flask import g
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return {"message": "User not found"}, 401
            g.current_user = user
            g.db = db
            try:
                return fn(*args, **kwargs)
            finally:
                # Remove g.db responsibility from routes, close here.
                db.close()
        except Exception:
            db.close()
            raise

    return wrapper


# PUBLIC_INTERFACE
def paginate(query, page: int, page_size: int):
    """Paginate a SQLAlchemy query returning items and metadata."""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if page_size else 1
    metadata = {
        "total": total,
        "total_pages": total_pages,
        "first_page": 1,
        "last_page": total_pages or 1,
        "page": page,
        "previous_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }
    return items, metadata
