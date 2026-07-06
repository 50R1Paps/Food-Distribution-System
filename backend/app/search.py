from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Family, Person, User
from app.schemas import FamilySearchResult, PersonSearchResult, SearchResult

router = APIRouter(
    prefix="/api",
    tags=["search"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/search", response_model=SearchResult)
def search(
    q: str = Query(..., min_length=1, description="Termine di ricerca"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    pattern = f"%{q}%"
    offset = (page - 1) * page_size

    family_query = db.query(Family).filter(Family.family_name.ilike(pattern))
    person_query = db.query(Person).filter(
        or_(
            Person.first_name.ilike(pattern),
            Person.last_name.ilike(pattern),
        )
    )

    family_total = family_query.count()
    person_total = person_query.count()
    total = family_total + person_total

    families = (
        family_query.order_by(Family.family_name)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    remaining = max(0, page_size - len(families))
    persons = (
        person_query.order_by(Person.last_name, Person.first_name)
        .offset(offset)
        .limit(remaining if remaining > 0 else page_size)
        .all()
    )

    return SearchResult(
        families=[FamilySearchResult.model_validate(f) for f in families],
        persons=[
            PersonSearchResult(
                id=p.id,
                first_name=p.first_name,
                last_name=p.last_name,
                fingerprint_id=p.fingerprint_id,
                family_id=p.family_id,
            )
            for p in persons
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
