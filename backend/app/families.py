from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Distribution, Family, Person, User
from app.schemas import (
    FamilyCreate,
    FamilyDetail,
    FamilyOut,
    FamilyPage,
    FamilyUpdate,
    MemberCreate,
    PersonOut,
    PersonUpdate,
)

router = APIRouter(
    prefix="/api",
    tags=["families"],
    dependencies=[Depends(get_current_user)],
)


def _get_family_or_404(db: Session, family_id: int) -> Family:
    family = db.get(Family, family_id)
    if family is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Famiglia non trovata",
        )
    return family


def _get_person_or_404(db: Session, person_id: int) -> Person:
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro non trovato",
        )
    return person


def _check_fingerprint_unique(db: Session, fingerprint_id: str | None, exclude_person_id: int | None = None) -> None:
    if not fingerprint_id:
        return
    query = db.query(Person).filter(Person.fingerprint_id == fingerprint_id)
    if exclude_person_id is not None:
        query = query.filter(Person.id != exclude_person_id)
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impronta digitale già registrata per un altro membro",
        )


@router.get("/families", response_model=FamilyPage)
def list_families(
    search: str | None = Query(None, description="Ricerca per nome famiglia"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Family)
    if search:
        query = query.filter(Family.family_name.ilike(f"%{search}%"))
    total = query.count()
    items = (
        query.order_by(Family.family_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return FamilyPage(items=items, total=total, page=page, page_size=page_size)


@router.post("/families", response_model=FamilyOut, status_code=status.HTTP_201_CREATED)
def create_family(payload: FamilyCreate, db: Session = Depends(get_db)):
    family = Family(**payload.model_dump())
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


@router.get("/families/{family_id}", response_model=FamilyDetail)
def get_family(family_id: int, db: Session = Depends(get_db)):
    family = (
        db.query(Family)
        .options(selectinload(Family.members), selectinload(Family.distributions))
        .filter(Family.id == family_id)
        .first()
    )
    if family is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Famiglia non trovata",
        )
    return family


@router.put("/families/{family_id}", response_model=FamilyOut)
def update_family(family_id: int, payload: FamilyUpdate, db: Session = Depends(get_db)):
    family = _get_family_or_404(db, family_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(family, field, value)
    db.commit()
    db.refresh(family)
    return family


@router.delete("/families/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_family(family_id: int, db: Session = Depends(get_db)):
    family = _get_family_or_404(db, family_id)
    has_distributions = (
        db.query(Distribution).filter(Distribution.family_id == family_id).first()
        is not None
    )
    if has_distributions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossibile eliminare: la famiglia ha distribuzioni registrate",
        )
    for member in family.members:
        db.delete(member)
    db.delete(family)
    db.commit()


@router.post(
    "/families/{family_id}/members",
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
)
def add_member(family_id: int, payload: MemberCreate, db: Session = Depends(get_db)):
    _get_family_or_404(db, family_id)
    _check_fingerprint_unique(db, payload.fingerprint_id)
    person = Person(**payload.model_dump(), family_id=family_id)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.put("/members/{person_id}", response_model=PersonOut)
def update_member(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db)):
    person = _get_person_or_404(db, person_id)
    data = payload.model_dump(exclude_unset=True)
    if "fingerprint_id" in data:
        _check_fingerprint_unique(db, data["fingerprint_id"], exclude_person_id=person_id)
    for field, value in data.items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person


@router.delete("/members/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(person_id: int, db: Session = Depends(get_db)):
    person = _get_person_or_404(db, person_id)
    has_distributions = (
        db.query(Distribution).filter(Distribution.person_id == person_id).first()
        is not None
    )
    if has_distributions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossibile eliminare: il membro ha distribuzioni registrate",
        )
    db.delete(person)
    db.commit()
