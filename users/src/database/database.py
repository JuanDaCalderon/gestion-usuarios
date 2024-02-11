import os
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

env_file = find_dotenv('.env')
loaded = load_dotenv(env_file)

print('********************************************************************************************************')
print('DB_USER->', os.environ.get("DB_USER"),
      'DB_PASSWORD->', os.environ.get("DB_PASSWORD"),
      'DB_HOST->', os.environ.get("DB_HOST"),
      'DB_NAME->', os.environ.get("DB_NAME"),
      'DB_PORT->', os.environ.get("DB_PORT"))
print('********************************************************************************************************')

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    username=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    database=os.environ.get("DB_NAME"),
    port=os.environ.get("DB_PORT")
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
