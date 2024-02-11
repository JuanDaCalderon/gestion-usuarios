from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database import database


class User(database.Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    phoneNumber = Column(String)
    dni = Column(String)
    fullName = Column(String)
    password = Column(String)
    salt = Column(String)
    token = Column(String)
    status = Column(String)
    expireAt = Column(DateTime)
    createdAt = Column(DateTime)
    updateAt = Column(DateTime)


database.Base.metadata.create_all(bind=database.engine)