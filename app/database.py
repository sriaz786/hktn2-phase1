"""Database session management."""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session

from app.config import get_session_factory

logger = logging.getLogger(__name__)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection.

    Yields:
        Session: SQLAlchemy session

    Example:
        with get_session() as session:
            # Use session
            pass
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Database session error, rolling back")
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database session.

    This is used with FastAPI's Depends() for route handlers.

    Yields:
        Session: SQLAlchemy session

    Example:
        @app.get("/todos")
        def get_todos(session: Session = Depends(get_db_session)):
            return session.exec(select(Todo)).all()
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
