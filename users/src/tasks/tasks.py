from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import uuid

from ..models import models
from ..schemas import schemas

from enum import Enum


class Status(Enum):
    POR_VERIFICAR = "POR_VERIFICAR"
    NO_VERIFICADO = "NO_VERIFICADO"
    VERIFICADO = "VERIFICADO"


def create_user(db: Session, user: schemas.UserCreate):
    password = user.password.encode()
    salt = Fernet.generate_key()
    f = Fernet(salt)
    hashed_password = f.encrypt(password)
    new_token = uuid.uuid4()
    now = datetime.fromisoformat(datetime.now(
        timezone.utc).isoformat("T", "seconds"))
    createdAt = now
    expireAt = now + timedelta(hours=1)
    new_user = models.User(username=user.username, email=user.email, password=hashed_password.decode(),
                           dni=user.dni, fullName=user.fullName, phoneNumber=user.phoneNumber,
                           salt=salt.decode(), token=new_token, status=Status.NO_VERIFICADO.value,
                           expireAt=expireAt, createdAt=createdAt, updateAt=createdAt)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def verify_if_user_already_exist(db: Session, username: str, email: str):
    user = db.query(models.User).filter(
        (models.User.username == username) | (models.User.email == email)).first()
    if user:
        return user
    else:
        return False


def verfiy_token(db: Session, token: str):
    user = db.query(models.User).filter(models.User.token == token).first()
    if user:
        now = datetime.now()
        expDate = user.expireAt
        if now < expDate:
            return user
        else:
            return False
    else:
        return False


def generate_token(db: Session, user: models.User, password: str):
    salt = str(user.salt).encode()
    f = Fernet(salt)
    db_password = f.decrypt(user.password)
    current_password = password.encode()
    if db_password == current_password:
        new_token = uuid.uuid4()
        now = datetime.fromisoformat(datetime.now(
            timezone.utc).isoformat("T", "seconds"))
        expireAt = now + timedelta(hours=1)
        db.query(models.User).filter(models.User.id == user.id).update(
            {models.User.token: new_token, models.User.expireAt: expireAt})
        db.commit()
        return True
    else:
        return False


def user_update(db: Session, id: str, userData: schemas.UserUpdate):
    original = userData.model_dump()
    updateAt = datetime.fromisoformat(datetime.now(
        timezone.utc).isoformat("T", "seconds"))
    filtered = {k: v for k, v in original.items() if v is not None}
    filtered['updateAt'] = updateAt
    count = db.query(models.User).filter(
        models.User.id == id).update(filtered)
    db.commit()
    if count > 0:
        return True
    else:
        return False


def reset_db(db: Session):
    db.query(models.User).delete()
    db.commit()
