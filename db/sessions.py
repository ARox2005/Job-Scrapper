from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager
# from sqlalchemy.orm import sessionmaker

import config

engine = create_engine(config.DATABASE, echo=True)

# Session = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

def init_db():
    """Create all tables in Postgres if they don't exist."""
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    """Provide a database session that auto-closes."""
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()