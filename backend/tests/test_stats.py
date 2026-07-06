import csv
import io
from datetime import date, datetime, timezone

import pytest

from app.models import Distribution, Family, PackageType, Person


@pytest.fixture()
def stats_data(db_session):
    pt = PackageType(name="Standard", cooldown_days=30, is_active=True)
    pt2 = PackageType(name="Emergency", cooldown_days=0, is_active=True)
    db_session.add_all([pt, pt2])
    db_session.commit()
    db_session.refresh(pt)
    db_session.refresh(pt2)

    fam1 = Family(family_name="Rossi", address="Via Roma 1")
    fam2 = Family(family_name="Bianchi", address="Via Nova 5")
    db_session.add_all([fam1, fam2])
    db_session.commit()
    db_session.refresh(fam1)
    db_session.refresh(fam2)

    p1 = Person(
        first_name="Mario", last_name="Rossi",
        date_of_birth=date(1980, 5, 10), fingerprint_id="FP-1",
        family_id=fam1.id,
    )
    p2 = Person(
        first_name="Luca", last_name="Bianchi",
        date_of_birth=date(1990, 1, 1), fingerprint_id="FP-2",
        family_id=fam2.id,
    )
    db_session.add_all([p1, p2])
    db_session.commit()
    db_session.refresh(p1)
    db_session.refresh(p2)

    now = datetime.now(timezone.utc)
    d1 = Distribution(family_id=fam1.id, person_id=p1.id, package_type="Standard")
    d2 = Distribution(family_id=fam1.id, person_id=p1.id, package_type="Emergency")
    d3 = Distribution(family_id=fam2.id, person_id=p2.id, package_type="Standard")
    db_session.add_all([d1, d2, d3])
    db_session.commit()

    return {"pt": pt, "pt2": pt2, "fam1": fam1, "fam2": fam2, "p1": p1, "p2": p2}


# --- Overview ---


def test_overview_requires_auth(client):
    assert client.get("/api/stats/overview").status_code == 401


def test_overview_empty_db(client, auth_headers):
    r = client.get("/api/stats/overview", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_families"] == 0
    assert data["total_persons"] == 0
    assert data["total_distributions"] == 0
    assert data["distributions_this_month"] == 0


def test_overview_with_data(client, auth_headers, stats_data):
    r = client.get("/api/stats/overview", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_families"] == 2
    assert data["total_persons"] == 2
    assert data["total_distributions"] == 3
    assert data["distributions_this_month"] == 3


# --- Distribution stats ---


def test_distribution_stats_requires_auth(client):
    assert client.get("/api/stats/distributions").status_code == 401


def test_distribution_stats_no_filter(client, auth_headers, stats_data):
    r = client.get("/api/stats/distributions", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    by_pt = {item["package_type"]: item["count"] for item in data["by_package_type"]}
    assert by_pt["Standard"] == 2
    assert by_pt["Emergency"] == 1


def test_distribution_stats_empty_db(client, auth_headers):
    r = client.get("/api/stats/distributions", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["by_package_type"] == []


def test_distribution_stats_date_filter(client, auth_headers, stats_data, db_session):
    future = datetime(2099, 1, 1, tzinfo=timezone.utc).isoformat()
    r = client.get(
        "/api/stats/distributions",
        headers=auth_headers,
        params={"date_from": future},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0


# --- Family coverage ---


def test_family_coverage_requires_auth(client):
    assert client.get("/api/stats/families").status_code == 401


def test_family_coverage_empty(client, auth_headers):
    r = client.get("/api/stats/families", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_families"] == 0
    assert data["families_served"] == 0
    assert data["families_not_served"] == 0


def test_family_coverage_with_data(client, auth_headers, stats_data):
    r = client.get("/api/stats/families", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_families"] == 2
    assert data["families_served"] == 2
    assert data["families_not_served"] == 0


def test_family_coverage_partial(client, auth_headers, db_session):
    fam1 = Family(family_name="Served", address="Via 1")
    fam2 = Family(family_name="NotServed", address="Via 2")
    db_session.add_all([fam1, fam2])
    db_session.commit()
    db_session.refresh(fam1)
    db_session.refresh(fam2)

    p = Person(
        first_name="Test", last_name="Test",
        date_of_birth=date(2000, 1, 1), family_id=fam1.id,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    d = Distribution(family_id=fam1.id, person_id=p.id, package_type="Standard")
    db_session.add(d)
    db_session.commit()

    r = client.get("/api/stats/families", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_families"] == 2
    assert data["families_served"] == 1
    assert data["families_not_served"] == 1


# --- Trends ---


def test_trends_requires_auth(client):
    assert client.get("/api/stats/trends").status_code == 401


def test_trends_empty(client, auth_headers):
    r = client.get("/api/stats/trends", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["granularity"] == "monthly"
    assert data["points"] == []


def test_trends_monthly(client, auth_headers, stats_data):
    r = client.get("/api/stats/trends", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["granularity"] == "monthly"
    assert len(data["points"]) == 1
    now = datetime.now(timezone.utc)
    expected_period = now.strftime("%Y-%m")
    assert data["points"][0]["period"] == expected_period
    assert data["points"][0]["count"] == 3


def test_trends_weekly(client, auth_headers, stats_data):
    r = client.get(
        "/api/stats/trends",
        headers=auth_headers,
        params={"granularity": "weekly"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["granularity"] == "weekly"
    assert len(data["points"]) == 1
    assert data["points"][0]["count"] == 3


# --- Reports ---


def test_distributions_report_requires_auth(client):
    assert client.get("/api/reports/distributions").status_code == 401


def test_distributions_report_csv(client, auth_headers, stats_data):
    r = client.get("/api/reports/distributions", headers=auth_headers)
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]

    reader = csv.reader(io.StringIO(r.text))
    rows = list(reader)
    assert rows[0][0] == "ID Distribuzione"
    assert len(rows) == 4  # header + 3 distributions
    assert rows[1][3] == "Mario Rossi"


def test_distributions_report_date_filter(client, auth_headers, stats_data):
    future = datetime(2099, 1, 1, tzinfo=timezone.utc).isoformat()
    r = client.get(
        "/api/reports/distributions",
        headers=auth_headers,
        params={"date_from": future},
    )
    assert r.status_code == 200
    reader = csv.reader(io.StringIO(r.text))
    rows = list(reader)
    assert len(rows) == 1  # only header


def test_families_report_requires_auth(client):
    assert client.get("/api/reports/families").status_code == 401


def test_families_report_csv(client, auth_headers, stats_data):
    r = client.get("/api/reports/families", headers=auth_headers)
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]

    reader = csv.reader(io.StringIO(r.text))
    rows = list(reader)
    assert rows[0][0] == "ID Famiglia"
    assert len(rows) == 3  # header + 2 families
    family_names = {rows[1][1], rows[2][1]}
    assert "Rossi" in family_names
    assert "Bianchi" in family_names


def test_families_report_shows_served_status(client, auth_headers, db_session):
    fam1 = Family(family_name="Served", address="Via 1")
    fam2 = Family(family_name="NotServed", address="Via 2")
    db_session.add_all([fam1, fam2])
    db_session.commit()
    db_session.refresh(fam1)
    db_session.refresh(fam2)

    p = Person(
        first_name="Test", last_name="Test",
        date_of_birth=date(2000, 1, 1), family_id=fam1.id,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    d = Distribution(family_id=fam1.id, person_id=p.id, package_type="Standard")
    db_session.add(d)
    db_session.commit()

    r = client.get("/api/reports/families", headers=auth_headers)
    assert r.status_code == 200
    reader = csv.reader(io.StringIO(r.text))
    rows = list(reader)
    assert len(rows) == 3
    served_row = next(row for row in rows[1:] if row[1] == "Served")
    not_served_row = next(row for row in rows[1:] if row[1] == "NotServed")
    assert served_row[6] == "Si"
    assert not_served_row[6] == "No"
