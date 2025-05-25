from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.security import create_access_token
from models.user import authenticate_user
from schemas.token import Token

router = APIRouter(
    tags=["authentication"],
)


@router.post(
    "/token",
    response_model=Token
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"name": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
