from fastapi import Depends, FastAPI, Header, status, HTTPException
from typing import Union
from starlette.responses import RedirectResponse
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from .schemas import schemas
from .tasks import tasks
from .database import database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 0.Root endpoint DONE


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return RedirectResponse(url="/docs/")


# 1.Creación de usuarios DONE
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_users(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if not user.username or not user.password or not user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="username, password, o email son campos obligatorios")
    else:
        username = user.username
        email = user.email
        user_db = tasks.verify_if_user_already_exist(
            db=db, email=email, username=username)
        if user_db:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED, detail="Este usuario ya existe con este Nombre de usuario y/o Email")
        else:
            new_user = tasks.create_user(db=db, user=user)
            return {
                "id": new_user.id,
                "createdAt": new_user.createdAt
            }


# 2.Actualización de usuarios DONE
@app.patch("/users/{id}", status_code=status.HTTP_200_OK)
def update_users(id: str, userData: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    if userData.status or userData.dni or userData.fullName or userData.phoneNumber:
        was_updated = tasks.user_update(db=db, id=id, userData=userData)
        if was_updated:
            return {"msg": "el usuario ha sido actualizado"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="El usuario con este ID no existe")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Al menos un campo debe ser pasado en el cuerpo de la petición")


# 3.Generación de token DONE
@app.post("/users/auth", status_code=status.HTTP_200_OK)
def generate_token(userGenerateToken: schemas.generateToken, db: Session = Depends(database.get_db)):
    if not userGenerateToken.username or not userGenerateToken.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="username y password son campos obligatorios")
    else:
        username = userGenerateToken.username
        user_db = tasks.verify_if_user_already_exist(
            db=db, email='', username=username)
        if user_db:
            token = tasks.generate_token(
                db=db, user=user_db, password=userGenerateToken.password)
            if token:
                return {
                    "id": user_db.id,
                    "token": user_db.token,
                    "expireAt": user_db.expireAt
                }
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Password incorrecto")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="username con este password no existe")

# 4.Consultar información del usuario DONE


@app.get("/users/me", status_code=status.HTTP_200_OK)
def check_me(Authorization: Annotated[Union[str, None], Header()] = None, db: Session = Depends(database.get_db)):
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="el token no fue suministrado en el header")
    else:
        given_token = Authorization.replace("Bearer", "").strip()
        user = tasks.verfiy_token(db=db, token=given_token)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "fullName": user.fullName,
                "dni": user.dni,
                "phoneNumber": user.phoneNumber,
                "status": user.status
            }
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="el token es invalido o ya expiro")


# 5.Consulta de salud del servicio DONE
@app.get("/users/ping", status_code=status.HTTP_200_OK)
def verify_health():
    return "pong"


# 6.Restablecer base de datos
@app.post("/users/reset", status_code=status.HTTP_200_OK)
def reset(db: Session = Depends(database.get_db)):
    tasks.reset_db(db=db)
    return {"msg": "Todos los datos fueron eliminados"}
