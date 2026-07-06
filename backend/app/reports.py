import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Distribution, Family, Person

router = APIRouter(
    prefix="/api/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)],
)


def _csv_response(content: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/distributions")
def distributions_report(
    date_from: datetime | None = Query(None, description="Data inizio (ISO)"),
    date_to: datetime | None = Query(None, description="Data fine (ISO)"),
    db: Session = Depends(get_db),
):
    query = db.query(Distribution, Family, Person).join(
        Family, Distribution.family_id == Family.id
    ).join(
        Person, Distribution.person_id == Person.id
    )

    if date_from:
        query = query.filter(Distribution.distribution_date >= date_from)
    if date_to:
        query = query.filter(Distribution.distribution_date <= date_to)

    query = query.order_by(Distribution.distribution_date)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID Distribuzione",
        "Data",
        "Famiglia",
        "Persona",
        "Tipo Pacco",
        "Note",
        "Emergenza",
    ])

    for dist, fam, person in query.all():
        writer.writerow([
            dist.id,
            dist.distribution_date.isoformat() if dist.distribution_date else "",
            fam.family_name,
            f"{person.first_name} {person.last_name}",
            dist.package_type,
            dist.notes or "",
            "Si" if dist.is_emergency else "No",
        ])

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return _csv_response(output.getvalue(), f"report_distribuzioni_{stamp}.csv")


@router.get("/families")
def families_report(db: Session = Depends(get_db)):
    families = db.query(Family).order_by(Family.family_name).all()

    served_ids = set(
        r[0]
        for r in db.query(Distribution.family_id).distinct().all()
    )

    member_counts: dict[int, int] = {}
    for fam in families:
        count = db.query(Person).filter(Person.family_id == fam.id).count()
        member_counts[fam.id] = count

    dist_counts: dict[int, int] = {}
    if families:
        rows = (
            db.query(Distribution.family_id)
            .filter(Distribution.family_id.in_([f.id for f in families]))
            .all()
        )
        for (fam_id,) in rows:
            dist_counts[fam_id] = dist_counts.get(fam_id, 0) + 1

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID Famiglia",
        "Nome Famiglia",
        "Indirizzo",
        "Telefono",
        "Numero Membri",
        "Numero Distribuzioni",
        "Servita",
    ])

    for fam in families:
        writer.writerow([
            fam.id,
            fam.family_name,
            fam.address,
            fam.contact_number or "",
            member_counts.get(fam.id, 0),
            dist_counts.get(fam.id, 0),
            "Si" if fam.id in served_ids else "No",
        ])

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return _csv_response(output.getvalue(), f"report_famiglie_{stamp}.csv")
