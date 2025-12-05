from fastapi import APIRouter, Depends
from pydantic import BaseModel

from Infrastructure.api.dependencies import get_user_service, get_auth_service
from Core_Domains.User_Security.services import UserService
from Core_Domains.User_Security.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["Users"])


class RegisterDTO(BaseModel):
    email: str
    password: str


class LoginDTO(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(dto: RegisterDTO, svc: UserService = Depends(get_user_service)):
    u = svc.register(dto.email, dto.password)
    return {"user_id": u.id}


@router.post("/login")
def login(dto: LoginDTO, auth: AuthService = Depends(get_auth_service)):
    user = auth.authenticate(dto.email, dto.password)
    return {"user_id": user.id, "status": "ok"}
