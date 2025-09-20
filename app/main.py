from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestionare sudori autorizati",
    description=(
        "API pentru evidenta sudorilor autorizati conform ASME Sectiunea IX si "
        "prescriptiilor ISCIR (CR9, CR7)."
    ),
    version="0.1.0",
)


@app.post("/welders", response_model=schemas.Welder, status_code=status.HTTP_201_CREATED)
def create_welder(
    welder_in: schemas.WelderCreate, db: Session = Depends(get_db)
) -> schemas.Welder:
    existing = crud.get_welder_by_identifier(db, welder_in.identifier)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exista deja un sudor cu acest identificator.",
        )
    welder = crud.create_welder(db, welder_in)
    return welder


@app.get("/welders", response_model=list[schemas.Welder])
def list_welders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.Welder]:
    welders = crud.list_welders(db, skip=skip, limit=limit)
    return list(welders)


@app.get("/welders/{welder_id}", response_model=schemas.Welder)
def get_welder(welder_id: int, db: Session = Depends(get_db)) -> schemas.Welder:
    welder = crud.get_welder(db, welder_id)
    if not welder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sudor inexistent")
    return welder


@app.put("/welders/{welder_id}", response_model=schemas.Welder)
def update_welder(
    welder_id: int, welder_in: schemas.WelderUpdate, db: Session = Depends(get_db)
) -> schemas.Welder:
    welder = crud.get_welder(db, welder_id)
    if not welder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sudor inexistent")
    if welder_in.identifier and welder_in.identifier != welder.identifier:
        if crud.get_welder_by_identifier(db, welder_in.identifier):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identificatorul apartine deja altui sudor.",
            )
    return crud.update_welder(db, welder, welder_in)


@app.delete("/welders/{welder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_welder(welder_id: int, db: Session = Depends(get_db)) -> None:
    welder = crud.get_welder(db, welder_id)
    if not welder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sudor inexistent")
    crud.delete_welder(db, welder)


@app.get(
    "/welders/{welder_id}/authorizations",
    response_model=list[schemas.Authorization],
)
def list_authorizations(
    welder_id: int, db: Session = Depends(get_db)
) -> list[schemas.Authorization]:
    welder = crud.get_welder(db, welder_id)
    if not welder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sudor inexistent")
    return list(crud.list_authorizations_for_welder(db, welder))


@app.post(
    "/welders/{welder_id}/authorizations",
    response_model=schemas.Authorization,
    status_code=status.HTTP_201_CREATED,
)
def create_authorization(
    welder_id: int,
    auth_in: schemas.AuthorizationCreate,
    db: Session = Depends(get_db),
) -> schemas.Authorization:
    welder = crud.get_welder(db, welder_id)
    if not welder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sudor inexistent")
    return crud.create_authorization(db, welder, auth_in)


@app.put("/authorizations/{authorization_id}", response_model=schemas.Authorization)
def update_authorization(
    authorization_id: int,
    auth_in: schemas.AuthorizationUpdate,
    db: Session = Depends(get_db),
) -> schemas.Authorization:
    authorization = crud.get_authorization(db, authorization_id)
    if not authorization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autorizatie inexistenta")
    return crud.update_authorization(db, authorization, auth_in)


@app.delete("/authorizations/{authorization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_authorization(authorization_id: int, db: Session = Depends(get_db)) -> None:
    authorization = crud.get_authorization(db, authorization_id)
    if not authorization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autorizatie inexistenta")
    crud.delete_authorization(db, authorization)


@app.get(
    "/authorizations/expiring",
    response_model=list[schemas.AuthorizationExpiring],
)
def expiring_authorizations(
    days: Annotated[int, Query(gt=0, le=365)] = 60,
    reference_date: Annotated[date | None, Query()] = None,
    db: Session = Depends(get_db),
) -> list[schemas.AuthorizationExpiring]:
    ref_date = reference_date or date.today()
    expiring = crud.list_expiring_authorizations(db, ref_date, days)
    return expiring


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "sqlite",
    }
