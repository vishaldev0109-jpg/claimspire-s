from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserOut
from app.security import create_token, get_current_user, verify_password

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/login', response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower().strip()))
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return TokenOut(access_token=create_token(user))

@router.get('/me', response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
