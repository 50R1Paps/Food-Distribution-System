from datetime import date, datetime, timedelta

import pytest

from app.models import Distribution, Family, PackageType, Person


@pytest.fixture()
def family(db_session):
    fam = Family(family_name="Rossi", address="Via Roma 1")
    db_session.add(fam)
    db_session.commit()
    db_session.refresh(fam)
    return fam


@pytest.fixture()
def person(db_session, family):
    p = Person(
        first_name="Mario",
        last_name="Rossi",
        date_of_birth=date(1980, 5, 10),
        fingerprint_id="FP-1",
        family_id=family.id,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture()
def package_type(db_session):
    pt = PackageType(name="Standard", cooldown_days=30, is_active=True)
    db_session.add(pt)
    db_session.commit()
    db_session.refresh(pt)
    return pt


# --- Package types ---


def test_package_types_require_auth(client):
    assert client.get("/api/package-types").status_code == 401


def test_list_package_types_only_active(client, auth_headers, db_session, package_type):
    db_session.add(PackageType(name="Vecchio", is_active=False))
    db_session.commit()

    r = client.get("/api/package-types", headers=auth_headers)
    assert r.status_code == 200
    names = [pt["name"] for pt in r.json()]
    assert names == ["Standard"]

    r = client.get("/api/package-types", headers=auth_headers, params={"include_inactive": True})
    assert len(r.json()) == 2


def test_create_package_type(client, auth_headers):
    r = client.post(
        "/api/package-types",
        headers=auth_headers,
        json={"name": "Freschi", "cooldown_days": 7},
    )
    assert r.status_code == 201
    assert r.json()["cooldown_days"] == 7


def test_create_package_type_duplicate_name(client, auth_headers, package_type):
    r = client.post("/api/package-types", headers=auth_headers, json={"name": "Standard"})
    assert r.status_code == 409


def test_update_package_type(client, auth_headers, package_type):
    r = client.put(
        f"/api/package-types/{package_type.id}",
        headers=auth_headers,
        json={"cooldown_days": 15},
    )
    assert r.status_code == 200
    assert r.json()["cooldown_days"] == 15


def test_deactivate_package_type(client, auth_headers, package_type):
    r = client.delete(f"/api/package-types/{package_type.id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_active"] is False


# --- Distributions ---


def test_create_distribution_by_person_id(client, auth_headers, person, package_type):
    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": person.id, "package_type_id": package_type.id},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["package_type"] == "Standard"
    assert data["family_name"] == "Rossi"
    assert data["person_name"] == "Mario Rossi"


def test_create_distribution_by_fingerprint(client, auth_headers, person, package_type):
    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"fingerprint_id": "FP-1", "package_type_id": package_type.id},
    )
    assert r.status_code == 201
    assert r.json()["person_id"] == person.id


def test_create_distribution_requires_identifier(client, auth_headers, package_type):
    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"package_type_id": package_type.id},
    )
    assert r.status_code == 422


def test_create_distribution_unknown_fingerprint(client, auth_headers, package_type):
    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"fingerprint_id": "FP-SCONOSCIUTA", "package_type_id": package_type.id},
    )
    assert r.status_code == 404


def test_cooldown_blocks_second_distribution(client, auth_headers, person, package_type):
    payload = {"person_id": person.id, "package_type_id": package_type.id}
    assert client.post("/api/distributions", headers=auth_headers, json=payload).status_code == 201

    r = client.post("/api/distributions", headers=auth_headers, json=payload)
    assert r.status_code == 409
    data = r.json()
    assert "warning" in data
    assert data["cooldown_days"] == 30


def test_emergency_overrides_cooldown(client, auth_headers, person, package_type):
    payload = {"person_id": person.id, "package_type_id": package_type.id}
    assert client.post("/api/distributions", headers=auth_headers, json=payload).status_code == 201

    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={**payload, "is_emergency": True},
    )
    assert r.status_code == 201
    assert r.json()["is_emergency"] is True


def test_cooldown_is_per_package_type(client, auth_headers, person, package_type, db_session):
    other = PackageType(name="Igiene", cooldown_days=60, is_active=True)
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)

    assert (
        client.post(
            "/api/distributions",
            headers=auth_headers,
            json={"person_id": person.id, "package_type_id": package_type.id},
        ).status_code
        == 201
    )
    # tipo diverso: nessun blocco
    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": person.id, "package_type_id": other.id},
    )
    assert r.status_code == 201


def test_cooldown_is_per_family(client, auth_headers, person, package_type, db_session, family):
    sibling = Person(
        first_name="Luigi",
        last_name="Rossi",
        date_of_birth=date(1985, 1, 1),
        family_id=family.id,
    )
    db_session.add(sibling)
    db_session.commit()
    db_session.refresh(sibling)

    assert (
        client.post(
            "/api/distributions",
            headers=auth_headers,
            json={"person_id": person.id, "package_type_id": package_type.id},
        ).status_code
        == 201
    )
    # altro membro della stessa famiglia: bloccato
    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": sibling.id, "package_type_id": package_type.id},
    )
    assert r.status_code == 409


def test_cooldown_expired_allows_distribution(client, auth_headers, person, package_type, db_session, family):
    old = Distribution(
        family_id=family.id,
        person_id=person.id,
        package_type="Standard",
        distribution_date=datetime.utcnow() - timedelta(days=31),
    )
    db_session.add(old)
    db_session.commit()

    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": person.id, "package_type_id": package_type.id},
    )
    assert r.status_code == 201


def test_inactive_package_type_rejected(client, auth_headers, person, package_type, db_session):
    package_type.is_active = False
    db_session.commit()

    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": person.id, "package_type_id": package_type.id},
    )
    assert r.status_code == 404


def test_get_distribution_receipt(client, auth_headers, person, package_type):
    r = client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": person.id, "package_type_id": package_type.id},
    )
    dist_id = r.json()["id"]

    r = client.get(f"/api/distributions/{dist_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["family_name"] == "Rossi"


def test_list_distributions_filters(client, auth_headers, person, package_type, db_session, family):
    other_fam = Family(family_name="Verdi", address="Via Napoli 3")
    db_session.add(other_fam)
    db_session.commit()
    other_person = Person(
        first_name="Anna",
        last_name="Verdi",
        date_of_birth=date(1990, 1, 1),
        family_id=other_fam.id,
    )
    db_session.add(other_person)
    db_session.commit()

    client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": person.id, "package_type_id": package_type.id},
    )
    client.post(
        "/api/distributions",
        headers=auth_headers,
        json={"person_id": other_person.id, "package_type_id": package_type.id},
    )

    r = client.get("/api/distributions", headers=auth_headers)
    assert r.json()["total"] == 2

    r = client.get("/api/distributions", headers=auth_headers, params={"family_id": family.id})
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["family_name"] == "Rossi"

    r = client.get(
        "/api/distributions",
        headers=auth_headers,
        params={"date_from": (datetime.utcnow() + timedelta(days=1)).isoformat()},
    )
    assert r.json()["total"] == 0
