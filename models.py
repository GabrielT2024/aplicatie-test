from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class WeldingStandard(str):
    ASME_IX = "ASME IX"
    CR9 = "CR9"
    CR7 = "CR7"


class Welder(Base):
    __tablename__ = "welders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    identifier: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    certification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    authorizations: Mapped[list[Authorization]] = relationship(
        "Authorization", back_populates="welder", cascade="all, delete-orphan"
    )


class Authorization(Base):
    __tablename__ = "authorizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    welder_id: Mapped[int] = mapped_column(ForeignKey("welders.id"))
    standard: Mapped[str] = mapped_column(
        Enum(
            WeldingStandard.ASME_IX,
            WeldingStandard.CR9,
            WeldingStandard.CR7,
            name="standard_enum",
        )
    )
    process: Mapped[str] = mapped_column(String(50))
    base_materials: Mapped[str | None] = mapped_column(String(100), nullable=True)
    filler_materials: Mapped[str | None] = mapped_column(String(100), nullable=True)
    thickness_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    position: Mapped[str | None] = mapped_column(String(50), nullable=True)
    joint_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    issue_date: Mapped[date] = mapped_column(Date)
    expiration_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    welder: Mapped[Welder] = relationship("Welder", back_populates="authorizations")
