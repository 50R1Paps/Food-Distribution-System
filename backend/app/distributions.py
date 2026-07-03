from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Distribution, PackageType, Person
from app.schemas import (
    CooldownWarning,
    DistributionCreate,
    DistributionPage,
    DistributionReceipt,
    PackageTypeCreate,
    PackageTypeOut,
    PackageTypeUpdate,
)

router = APIRouter(
    prefix="/api",
    tags=["distributions"],
    dependencies=[Depends(get_current_user)],
)


def _to_receipt(dist: Distribution) -> DistributionReceipt:
    return DistributionReceipt(
        id=dist.id,
        family_id=dist.family_id,
        person_id=dist.person_id,
        package_type=dist.package_type,
        distribution_date=dist.distribution_date,
        notes=dist.notes,
        is_emergency=dist.is_emergency,
        family_name=dist.family.family_name,
        person_name=f"{dist.person.first_name} {dist.person.last_name}",
    )


# --- Package types ---


@router.get("/package-types", response_model=list[PackageTypeOut])
def list_package_types(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(PackageType)
    if not include_inactive:
        query = query.filter(PackageType.is_active.is_(True))
    return query.order_by(PackageType.name).all()


@router.post("/package-types", response_model=PackageTypeOut, status_code=status.HTTP_201_CREATED)
def create_package_type(payload: PackageTypeCreate, db: Session = Depends(get_db)):
    existing = db.query(PackageType).filter(PackageType.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esiste già un tipo di pacco con questo nome",
        )
    package_type = PackageType(**payload.model_dump())
    db.add(package_type)
    db.commit()
    db.refresh(package_type)
    return package_type


@router.put("/package-types/{package_type_id}", response_model=PackageTypeOut)
def update_package_type(
    package_type_id: int,
    payload: PackageTypeUpdate,
    db: Session = Depends(get_db),
):
    package_type = db.get(PackageType, package_type_id)
    if package_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo di pacco non trovato",
        )
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        duplicate = (
            db.query(PackageType)
            .filter(PackageType.name == data["name"], PackageType.id != package_type_id)
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esiste già un tipo di pacco con questo nome",
            )
    for field, value in data.items():
        setattr(package_type, field, value)
    db.commit()
    db.refresh(package_type)
    return package_type


@router.delete("/package-types/{package_type_id}", response_model=PackageTypeOut)
def deactivate_package_type(package_type_id: int, db: Session = Depends(get_db)):
    package_type = db.get(PackageType, package_type_id)
    if package_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo di pacco non trovato",
        )
    package_type.is_active = False
    db.commit()
    db.refresh(package_type)
    return package_type


# --- Distributions ---


@router.get("/distributions", response_model=DistributionPage)
def list_distributions(
    family_id: int | None = Query(None),
    package_type: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Distribution)
    if family_id is not None:
        query = query.filter(Distribution.family_id == family_id)
    if package_type:
        query = query.filter(Distribution.package_type == package_type)
    if date_from is not None:
        query = query.filter(Distribution.distribution_date >= date_from)
    if date_to is not None:
        query = query.filter(Distribution.distribution_date <= date_to)
    total = query.count()
    items = (
        query.order_by(Distribution.distribution_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return DistributionPage(
        items=[_to_receipt(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/distributions/{distribution_id}", response_model=DistributionReceipt)
def get_distribution(distribution_id: int, db: Session = Depends(get_db)):
    dist = db.get(Distribution, distribution_id)
    if dist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Distribuzione non trovata",
        )
    return _to_receipt(dist)


@router.post(
    "/distributions",
    response_model=DistributionReceipt,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": CooldownWarning}},
)
def create_distribution(payload: DistributionCreate, db: Session = Depends(get_db)):
    # identifica il destinatario per person_id o fingerprint_id
    if payload.person_id is not None:
        person = db.get(Person, payload.person_id)
    elif payload.fingerprint_id:
        person = (
            db.query(Person)
            .filter(Person.fingerprint_id == payload.fingerprint_id)
            .first()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Specificare person_id o fingerprint_id",
        )
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona non trovata",
        )

    package_type = db.get(PackageType, payload.package_type_id)
    if package_type is None or not package_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo di pacco non trovato o non attivo",
        )

    # cooldown per tipo di pacco, a livello di famiglia
    if not payload.is_emergency:
        last = (
            db.query(Distribution)
            .filter(
                Distribution.family_id == person.family_id,
                Distribution.package_type == package_type.name,
            )
            .order_by(Distribution.distribution_date.desc())
            .first()
        )
        if last is not None:
            next_allowed = last.distribution_date + timedelta(days=package_type.cooldown_days)
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            if now < next_allowed:
                warning = CooldownWarning(
                    warning=(
                        f"La famiglia ha già ricevuto '{package_type.name}' il "
                        f"{last.distribution_date.strftime('%d/%m/%Y')}. "
                        f"Prossima distribuzione consentita dal {next_allowed.strftime('%d/%m/%Y')}."
                    ),
                    last_distribution_date=last.distribution_date,
                    cooldown_days=package_type.cooldown_days,
                    next_allowed_date=next_allowed,
                )
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=warning.model_dump(mode="json"),
                )

    dist = Distribution(
        family_id=person.family_id,
        person_id=person.id,
        package_type=package_type.name,
        notes=payload.notes,
        is_emergency=payload.is_emergency,
    )
    db.add(dist)
    db.commit()
    db.refresh(dist)
    return _to_receipt(dist)
