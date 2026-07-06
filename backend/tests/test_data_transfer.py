from datetime import date, datetime, timezone

import pytest

from app.models import Distribution, Family, PackageType, Person


@pytest.fixture()
def sample_data(db_session):
    pt = PackageType(name="Standard", cooldown_days=30, is_active=True)
    db_session.add(pt)
    db_session.commit()
    db_session.refresh(pt)

    fam = Family(family_name="Rossi", address="Via Roma 1", contact_number="123")
    db_session.add(fam)
    db_session.commit()
    db_session.refresh(fam)

    person = Person(
        first_name="Mario",
        last_name="Rossi",
        date_of_birth=date(1980, 5, 10),
        fingerprint_id="FP-1",
        family_id=fam.id,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)

    dist = Distribution(
        family_id=fam.id,
        person_id=person.id,
        package_type="Standard",
    )
    db_session.add(dist)
    db_session.commit()
    db_session.refresh(dist)

    return {"pt": pt, "fam": fam, "person": person, "dist": dist}


def make_export_payload(data: dict) -> dict:
    return {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "package_types": [
            {
                "id": data["pt"].id,
                "name": data["pt"].name,
                "description": data["pt"].description,
                "cooldown_days": data["pt"].cooldown_days,
                "is_active": data["pt"].is_active,
            }
        ],
        "families": [
            {
                "id": data["fam"].id,
                "family_name": data["fam"].family_name,
                "address": data["fam"].address,
                "contact_number": data["fam"].contact_number,
                "created_at": data["fam"].created_at.isoformat(),
            }
        ],
        "persons": [
            {
                "id": data["person"].id,
                "first_name": data["person"].first_name,
                "last_name": data["person"].last_name,
                "date_of_birth": data["person"].date_of_birth.isoformat(),
                "fingerprint_id": data["person"].fingerprint_id,
                "family_id": data["person"].family_id,
                "created_at": data["person"].created_at.isoformat(),
            }
        ],
        "distributions": [
            {
                "id": data["dist"].id,
                "family_id": data["dist"].family_id,
                "person_id": data["dist"].person_id,
                "package_type": data["dist"].package_type,
                "distribution_date": data["dist"].distribution_date.isoformat(),
                "notes": data["dist"].notes,
                "is_emergency": data["dist"].is_emergency,
            }
        ],
    }


# --- Export ---


def test_export_requires_auth(client):
    assert client.get("/api/export").status_code == 401


def test_export_returns_json_file(client, auth_headers, sample_data):
    r = client.get("/api/export", headers=auth_headers)
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")
    assert r.headers["content-type"] == "application/json"

    data = r.json()
    assert data["version"] == 1
    assert "exported_at" in data
    assert len(data["package_types"]) == 1
    assert len(data["families"]) == 1
    assert len(data["persons"]) == 1
    assert len(data["distributions"]) == 1
    assert data["families"][0]["family_name"] == "Rossi"


def test_export_empty_db(client, auth_headers):
    r = client.get("/api/export", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["package_types"] == []
    assert data["families"] == []
    assert data["persons"] == []
    assert data["distributions"] == []


# --- Import: validation ---


def test_import_requires_auth(client):
    r = client.post("/api/import", json={"version": 1})
    assert r.status_code == 401


def test_import_invalid_json_structure(client, auth_headers):
    r = client.post("/api/import", headers=auth_headers, json={"bad": "structure"})
    assert r.status_code == 422


# --- Import: dry-run ---


def test_import_dry_run_merge_detects_existing(client, auth_headers, sample_data):
    payload = make_export_payload(sample_data)
    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": True, "mode": "merge"},
        json=payload,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["dry_run"] is True
    assert data["mode"] == "merge"
    assert data["summary"]["package_types"]["existing"] == 1
    assert data["summary"]["families"]["existing"] == 1
    assert data["summary"]["persons"]["existing"] == 1
    assert data["summary"]["distributions"]["existing"] == 1
    assert len(data["conflicts"]) >= 1


def test_import_dry_run_new_data(client, auth_headers):
    payload = {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "package_types": [
            {"id": 1, "name": "Nuovo", "cooldown_days": 15, "is_active": True},
        ],
        "families": [
            {"id": 1, "family_name": "Bianchi", "address": "Via Nova 5", "contact_number": None, "created_at": datetime.now(timezone.utc).isoformat()},
        ],
        "persons": [
            {"id": 1, "first_name": "Luca", "last_name": "Bianchi", "date_of_birth": "1990-01-01", "fingerprint_id": None, "family_id": 1, "created_at": datetime.now(timezone.utc).isoformat()},
        ],
        "distributions": [],
    }
    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": True, "mode": "merge"},
        json=payload,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["package_types"]["new"] == 1
    assert data["summary"]["families"]["new"] == 1
    assert data["summary"]["persons"]["new"] == 1
    assert data["summary"]["distributions"]["new"] == 0
    assert len(data["conflicts"]) == 0


# --- Import: merge mode ---


def test_import_merge_adds_new_data(client, auth_headers, db_session):
    payload = {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "package_types": [
            {"id": 1, "name": "Standard", "cooldown_days": 30, "is_active": True},
        ],
        "families": [
            {"id": 1, "family_name": "Rossi", "address": "Via Roma 1", "contact_number": None, "created_at": datetime.now(timezone.utc).isoformat()},
        ],
        "persons": [
            {"id": 1, "first_name": "Mario", "last_name": "Rossi", "date_of_birth": "1980-05-10", "fingerprint_id": "FP-1", "family_id": 1, "created_at": datetime.now(timezone.utc).isoformat()},
        ],
        "distributions": [],
    }
    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": False, "mode": "merge"},
        json=payload,
    )
    assert r.status_code == 200
    assert r.json()["dry_run"] is False

    assert db_session.query(PackageType).filter(PackageType.name == "Standard").count() == 1
    assert db_session.query(Family).filter(Family.family_name == "Rossi").count() == 1
    assert db_session.query(Person).filter(Person.fingerprint_id == "FP-1").count() == 1


def test_import_merge_skips_existing_package_type(client, auth_headers, db_session, sample_data):
    payload = {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "package_types": [
            {"id": 999, "name": "Standard", "cooldown_days": 99, "is_active": True},
        ],
        "families": [],
        "persons": [],
        "distributions": [],
    }
    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": False, "mode": "merge"},
        json=payload,
    )
    assert r.status_code == 200
    pt = db_session.query(PackageType).filter(PackageType.name == "Standard").first()
    assert pt.cooldown_days == 30  # not overwritten


def test_import_merge_remaps_foreign_keys(client, auth_headers, db_session):
    payload = {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "package_types": [
            {"id": 1, "name": "Standard", "cooldown_days": 30, "is_active": True},
        ],
        "families": [
            {"id": 100, "family_name": "Verdi", "address": "Via Verdi 1", "contact_number": None, "created_at": datetime.now(timezone.utc).isoformat()},
        ],
        "persons": [
            {"id": 200, "first_name": "Anna", "last_name": "Verdi", "date_of_birth": "1990-01-01", "fingerprint_id": "FP-200", "family_id": 100, "created_at": datetime.now(timezone.utc).isoformat()},
        ],
        "distributions": [
            {"id": 300, "family_id": 100, "person_id": 200, "package_type": "Standard", "distribution_date": datetime.now(timezone.utc).isoformat(), "notes": None, "is_emergency": False},
        ],
    }
    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": False, "mode": "merge"},
        json=payload,
    )
    assert r.status_code == 200

    fam = db_session.query(Family).filter(Family.family_name == "Verdi").first()
    assert fam is not None
    person = db_session.query(Person).filter(Person.fingerprint_id == "FP-200").first()
    assert person is not None
    assert person.family_id == fam.id
    dist = db_session.query(Distribution).filter(Distribution.person_id == person.id).first()
    assert dist is not None
    assert dist.family_id == fam.id


# --- Import: replace mode ---


def test_import_replace_wipes_and_reinserts(client, auth_headers, db_session, sample_data):
    db_session.add(Family(family_name="Extra", address="Via Extra 1"))
    db_session.commit()

    payload = make_export_payload(sample_data)
    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": False, "mode": "replace"},
        json=payload,
    )
    assert r.status_code == 200

    families = db_session.query(Family).all()
    assert len(families) == 1
    assert families[0].family_name == "Rossi"


def test_import_replace_preserves_ids(client, auth_headers, db_session, sample_data):
    payload = make_export_payload(sample_data)
    original_fam_id = sample_data["fam"].id
    original_pt_id = sample_data["pt"].id

    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": False, "mode": "replace"},
        json=payload,
    )
    assert r.status_code == 200

    fam = db_session.get(Family, original_fam_id)
    assert fam is not None
    assert fam.family_name == "Rossi"
    pt = db_session.get(PackageType, original_pt_id)
    assert pt is not None


# --- Import: transactional rollback ---


def test_import_duplicate_unique_key_rolls_back(client, auth_headers, db_session, sample_data):
    payload = {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "package_types": [
            {"id": 1, "name": "Dup", "cooldown_days": 30, "is_active": True},
            {"id": 2, "name": "Dup", "cooldown_days": 30, "is_active": True},
        ],
        "families": [],
        "persons": [],
        "distributions": [],
    }
    r = client.post(
        "/api/import",
        headers=auth_headers,
        params={"dry_run": False, "mode": "replace"},
        json=payload,
    )
    assert r.status_code == 500
    assert db_session.query(Family).filter(Family.family_name == "Rossi").count() == 1
