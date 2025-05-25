from pydantic import BaseModel


class Token(BaseModel):
    """Schema for the token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for the token data"""
    username: str | None = None


class TokenRequest(BaseModel):
    """Schema for the token request via JSON"""
    username: str
    password: str