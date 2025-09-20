from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

StandardLiteral = Literal["ASME IX", "CR9", "CR7"]


class AuthorizationBase(BaseModel):
    standard: StandardLiteral
    process: str = Field(..., description="Proces de sudura (ex. 111, 141)")
    base_materials: Optional[str] = Field(
        None, description="Materiale de baza acoperite de autorizare"
    )
    filler_materials: Optional[str] = Field(
        None, description="Materiale de adaos avizate"
    )
    thickness_range: Optional[str] = Field(
        None, description="Domeniul de grosimi calificat"
    )
    position: Optional[str] = Field(None, description="Pozitii de sudare")
    joint_type: Optional[str] = Field(None, description="Tipul imbinarii")
    notes: Optional[str] = Field(None, description="Observatii suplimentare")
    issue_date: date
    expiration_date: date


class AuthorizationCreate(AuthorizationBase):
    pass


class AuthorizationUpdate(BaseModel):
    standard: Optional[StandardLiteral]
    process: Optional[str]
    base_materials: Optional[str]
    filler_materials: Optional[str]
    thickness_range: Optional[str]
    position: Optional[str]
    joint_type: Optional[str]
    notes: Optional[str]
    issue_date: Optional[date]
    expiration_date: Optional[date]


class Authorization(AuthorizationBase):
    id: int
    welder_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WelderBase(BaseModel):
    first_name: str
    last_name: str
    identifier: str = Field(..., description="Cod intern sau CNP")
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    certification_date: Optional[date] = None
    status: str = Field("active", description="active/inactive/suspendat")


class WelderCreate(WelderBase):
    authorizations: list[AuthorizationCreate] | None = None


class WelderUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    identifier: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    certification_date: Optional[date]
    status: Optional[str]


class Welder(WelderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    authorizations: list[Authorization] = Field(default_factory=list)

    class Config:
        orm_mode = True


class AuthorizationExpiring(BaseModel):
    authorization: Authorization
    days_until_expiration: int
