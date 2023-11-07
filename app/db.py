from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

database_url = URL.create(
    drivername="postgresql",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)

engine = create_engine(database_url)


Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)  # pyright: ignore[reportGeneralTypeIssues]


Session = sessionmaker(bind=engine)
session = Session()
