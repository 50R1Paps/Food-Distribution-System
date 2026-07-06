from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Distribution, Family, PackageType, Person
from app.schemas import (
    ExportData,
    ImportConflict,
    ImportPreview,
    ImportSummaryEntry,
)

router = APIRouter(
    prefix="/api",
    tags=["data-transfer"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    package_types = db.query(PackageType).order_by(PackageType.id).all()
    families = db.query(Family).order_by(Family.id).all()
    persons = db.query(Person).order_by(Person.id).all()
    distributions = db.query(Distribution).order_by(Distribution.id).all()

    data = ExportData(
        exported_at=datetime.now(timezone.utc),
        package_types=package_types,
        families=families,
        persons=persons,
        distributions=distributions,
    )

    json_bytes = data.model_dump_json(indent=2).encode("utf-8")
    filename = f"export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _validate_payload(payload: dict) -> ExportData:
    try:
        return ExportData.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"JSON non valido: {exc.errors()[0]['msg']}",
        )


def _build_preview(data: ExportData, db: Session, mode: str) -> ImportPreview:
    summary: dict[str, ImportSummaryEntry] = {
        "package_types": ImportSummaryEntry(),
        "families": ImportSummaryEntry(),
        "persons": ImportSummaryEntry(),
        "distributions": ImportSummaryEntry(),
    }
    conflicts: list[ImportConflict] = []

    existing_pt_names = {pt.name for pt in db.query(PackageType).all()}
    for pt in data.package_types:
        if pt.name in existing_pt_names:
            summary["package_types"].existing += 1
            conflicts.append(
                ImportConflict(
                    entity="package_type",
                    identifier=pt.name,
                    message="Tipo di pacco già esistente",
                )
            )
        else:
            summary["package_types"].new += 1

    existing_family_ids = {f.id for f in db.query(Family.id).all()}
    for fam in data.families:
        if fam.id in existing_family_ids:
            summary["families"].existing += 1
            conflicts.append(
                ImportConflict(
                    entity="family",
                    identifier=str(fam.id),
                    message="Famiglia già esistente",
                )
            )
        else:
            summary["families"].new += 1

    existing_person_fps = {
        p.fingerprint_id for p in db.query(Person.fingerprint_id).all() if p.fingerprint_id
    }
    for p in data.persons:
        if p.fingerprint_id and p.fingerprint_id in existing_person_fps:
            summary["persons"].existing += 1
            conflicts.append(
                ImportConflict(
                    entity="person",
                    identifier=p.fingerprint_id,
                    message="Impronta digitale già registrata",
                )
            )
        else:
            summary["persons"].new += 1

    existing_dist_ids = {d.id for d in db.query(Distribution.id).all()}
    for d in data.distributions:
        if d.id in existing_dist_ids:
            summary["distributions"].existing += 1
        else:
            summary["distributions"].new += 1

    return ImportPreview(
        dry_run=True,
        mode=mode,
        summary=summary,
        conflicts=conflicts,
    )


def _do_replace(data: ExportData, db: Session) -> None:
    db.query(Distribution).delete()
    db.query(Person).delete()
    db.query(Family).delete()
    db.query(PackageType).delete()
    db.flush()

    for pt in data.package_types:
        db.add(PackageType(
            id=pt.id,
            name=pt.name,
            description=pt.description,
            cooldown_days=pt.cooldown_days,
            is_active=pt.is_active,
        ))
    db.flush()

    for fam in data.families:
        db.add(Family(
            id=fam.id,
            family_name=fam.family_name,
            address=fam.address,
            contact_number=fam.contact_number,
            created_at=fam.created_at,
        ))
    db.flush()

    for p in data.persons:
        db.add(Person(
            id=p.id,
            first_name=p.first_name,
            last_name=p.last_name,
            date_of_birth=p.date_of_birth,
            fingerprint_id=p.fingerprint_id,
            family_id=p.family_id,
            created_at=p.created_at,
        ))
    db.flush()

    for d in data.distributions:
        db.add(Distribution(
            id=d.id,
            family_id=d.family_id,
            person_id=d.person_id,
            package_type=d.package_type,
            distribution_date=d.distribution_date,
            notes=d.notes,
            is_emergency=d.is_emergency,
        ))


def _do_merge(data: ExportData, db: Session) -> None:
    existing_pt_names = {pt.name for pt in db.query(PackageType).all()}
    for pt in data.package_types:
        if pt.name not in existing_pt_names:
            db.add(PackageType(
                name=pt.name,
                description=pt.description,
                cooldown_days=pt.cooldown_days,
                is_active=pt.is_active,
            ))
    db.flush()

    family_id_map: dict[int, int] = {}
    for fam in data.families:
        existing = db.get(Family, fam.id)
        if existing is not None:
            family_id_map[fam.id] = existing.id
            continue
        new_fam = Family(
            family_name=fam.family_name,
            address=fam.address,
            contact_number=fam.contact_number,
        )
        db.add(new_fam)
        db.flush()
        family_id_map[fam.id] = new_fam.id

    person_id_map: dict[int, int] = {}
    existing_fps = {
        p.fingerprint_id for p in db.query(Person.fingerprint_id).all() if p.fingerprint_id
    }
    for p in data.persons:
        if p.fingerprint_id and p.fingerprint_id in existing_fps:
            existing_person = (
                db.query(Person)
                .filter(Person.fingerprint_id == p.fingerprint_id)
                .first()
            )
            if existing_person:
                person_id_map[p.id] = existing_person.id
                continue
        new_person = Person(
            first_name=p.first_name,
            last_name=p.last_name,
            date_of_birth=p.date_of_birth,
            fingerprint_id=p.fingerprint_id,
            family_id=family_id_map.get(p.family_id, p.family_id),
        )
        db.add(new_person)
        db.flush()
        person_id_map[p.id] = new_person.id
        if p.fingerprint_id:
            existing_fps.add(p.fingerprint_id)

    existing_dist_ids = {d.id for d in db.query(Distribution.id).all()}
    for d in data.distributions:
        if d.id in existing_dist_ids:
            continue
        db.add(Distribution(
            family_id=family_id_map.get(d.family_id, d.family_id),
            person_id=person_id_map.get(d.person_id, d.person_id),
            package_type=d.package_type,
            distribution_date=d.distribution_date,
            notes=d.notes,
            is_emergency=d.is_emergency,
        ))


@router.post("/import", response_model=ImportPreview)
def import_data(
    payload: dict,
    dry_run: bool = Query(True, description="Anteprima senza modificare i dati"),
    mode: str = Query("merge", pattern="^(merge|replace)$"),
    db: Session = Depends(get_db),
):
    data = _validate_payload(payload)

    if dry_run:
        return _build_preview(data, db, mode)

    try:
        if mode == "replace":
            _do_replace(data, db)
        else:
            _do_merge(data, db)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante l'importazione, operazione annullata",
        )

    preview = _build_preview(data, db, mode)
    preview.dry_run = False
    return preview
