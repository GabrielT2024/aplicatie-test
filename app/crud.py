from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def create_welder(db: Session, welder_in: schemas.WelderCreate) -> models.Welder:
    welder = models.Welder(
        first_name=welder_in.first_name,
        last_name=welder_in.last_name,
        identifier=welder_in.identifier,
        phone=welder_in.phone,
        email=welder_in.email,
        certification_date=welder_in.certification_date,
        status=welder_in.status,
    )
    if welder_in.authorizations:
        for auth_in in welder_in.authorizations:
            welder.authorizations.append(
                models.Authorization(
                    standard=auth_in.standard,
                    process=auth_in.process,
                    base_materials=auth_in.base_materials,
                    filler_materials=auth_in.filler_materials,
                    thickness_range=auth_in.thickness_range,
                    position=auth_in.position,
                    joint_type=auth_in.joint_type,
                    notes=auth_in.notes,
                    issue_date=auth_in.issue_date,
                    expiration_date=auth_in.expiration_date,
                )
            )
    db.add(welder)
    db.commit()
    db.refresh(welder)
    return welder


def get_welder(db: Session, welder_id: int) -> models.Welder | None:
    return db.get(models.Welder, welder_id)


def get_welder_by_identifier(db: Session, identifier: str) -> models.Welder | None:
    stmt = select(models.Welder).where(models.Welder.identifier == identifier)
    return db.scalar(stmt)


def list_welders(db: Session, skip: int = 0, limit: int = 100) -> Sequence[models.Welder]:
    stmt = select(models.Welder).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def update_welder(
    db: Session, welder: models.Welder, welder_in: schemas.WelderUpdate
) -> models.Welder:
    for field, value in welder_in.dict(exclude_unset=True).items():
        setattr(welder, field, value)
    db.add(welder)
    db.commit()
    db.refresh(welder)
    return welder


def delete_welder(db: Session, welder: models.Welder) -> None:
    db.delete(welder)
    db.commit()


def create_authorization(
    db: Session, welder: models.Welder, auth_in: schemas.AuthorizationCreate
) -> models.Authorization:
    authorization = models.Authorization(
        welder=welder,
        standard=auth_in.standard,
        process=auth_in.process,
        base_materials=auth_in.base_materials,
        filler_materials=auth_in.filler_materials,
        thickness_range=auth_in.thickness_range,
        position=auth_in.position,
        joint_type=auth_in.joint_type,
        notes=auth_in.notes,
        issue_date=auth_in.issue_date,
        expiration_date=auth_in.expiration_date,
    )
    db.add(authorization)
    db.commit()
    db.refresh(authorization)
    return authorization


def get_authorization(db: Session, authorization_id: int) -> models.Authorization | None:
    return db.get(models.Authorization, authorization_id)


def list_authorizations_for_welder(
    db: Session, welder: models.Welder
) -> Sequence[models.Authorization]:
    return welder.authorizations


def update_authorization(
    db: Session,
    authorization: models.Authorization,
    auth_in: schemas.AuthorizationUpdate,
) -> models.Authorization:
    for field, value in auth_in.dict(exclude_unset=True).items():
        setattr(authorization, field, value)
    db.add(authorization)
    db.commit()
    db.refresh(authorization)
    return authorization


def delete_authorization(db: Session, authorization: models.Authorization) -> None:
    db.delete(authorization)
    db.commit()


def list_expiring_authorizations(
    db: Session, reference_date: date, days: int
) -> list[schemas.AuthorizationExpiring]:
    deadline = reference_date + timedelta(days=days)
    stmt = select(models.Authorization).where(
        models.Authorization.expiration_date <= deadline
    )
    authorizations = db.scalars(stmt).all()

    result: list[schemas.AuthorizationExpiring] = []
    for authorization in authorizations:
        days_until = (authorization.expiration_date - reference_date).days
        if days_until >= 0:
            result.append(
                schemas.AuthorizationExpiring(
                    authorization=authorization, days_until_expiration=days_until
                )
            )
    return result
