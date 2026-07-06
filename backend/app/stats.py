from datetime import datetime, timezone
from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Distribution, Family, Person
from app.schemas import (
    DistributionStats,
    FamilyCoverageStats,
    OverviewStats,
    PackageTypeStat,
    TrendPoint,
    TrendsStats,
)

router = APIRouter(
    prefix="/api/stats",
    tags=["stats"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/overview", response_model=OverviewStats)
def overview(db: Session = Depends(get_db)):
    total_families = db.query(func.count(Family.id)).scalar() or 0
    total_persons = db.query(func.count(Person.id)).scalar() or 0
    total_distributions = db.query(func.count(Distribution.id)).scalar() or 0

    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    distributions_this_month = (
        db.query(func.count(Distribution.id))
        .filter(Distribution.distribution_date >= month_start)
        .scalar()
        or 0
    )

    return OverviewStats(
        total_families=total_families,
        total_persons=total_persons,
        total_distributions=total_distributions,
        distributions_this_month=distributions_this_month,
    )


@router.get("/distributions", response_model=DistributionStats)
def distribution_stats(
    date_from: datetime | None = Query(None, description="Data inizio (ISO)"),
    date_to: datetime | None = Query(None, description="Data fine (ISO)"),
    db: Session = Depends(get_db),
):
    query = db.query(
        Distribution.package_type,
        func.count(Distribution.id).label("count"),
    )

    if date_from:
        query = query.filter(Distribution.distribution_date >= date_from)
    if date_to:
        query = query.filter(Distribution.distribution_date <= date_to)

    rows = query.group_by(Distribution.package_type).all()

    by_pt = [PackageTypeStat(package_type=r.package_type, count=r.count) for r in rows]
    total = sum(r.count for r in rows)

    return DistributionStats(total=total, by_package_type=by_pt)


@router.get("/families", response_model=FamilyCoverageStats)
def family_coverage(db: Session = Depends(get_db)):
    total_families = db.query(func.count(Family.id)).scalar() or 0

    served_ids = (
        db.query(Distribution.family_id)
        .distinct()
        .subquery()
    )
    families_served = db.query(func.count()).select_from(served_ids).scalar() or 0

    return FamilyCoverageStats(
        total_families=total_families,
        families_served=families_served,
        families_not_served=total_families - families_served,
    )


@router.get("/trends", response_model=TrendsStats)
def trends(
    granularity: str = Query("monthly", pattern="^(monthly|weekly)$"),
    db: Session = Depends(get_db),
):
    rows = db.query(Distribution.distribution_date).all()

    counts: dict[str, int] = defaultdict(int)
    for (dt,) in rows:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if granularity == "weekly":
            iso_year, iso_week, _ = dt.isocalendar()
            period = f"{iso_year}-W{iso_week:02d}"
        else:
            period = dt.strftime("%Y-%m")

        counts[period] += 1

    points = [
        TrendPoint(period=p, count=c)
        for p, c in sorted(counts.items())
    ]

    return TrendsStats(granularity=granularity, points=points)
