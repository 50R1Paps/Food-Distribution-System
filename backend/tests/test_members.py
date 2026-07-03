from datetime import date

import pytest

from app.models import Distribution, Family, Person


@pytest.fixture()
def family(db_session):
    fam = Family(family_name="Rossi", address="Via Roma 1")
    db_session.add(fam)
    db_session.commit()
    db_session.refresh(fam)
    return fam


@pytest.fixture()
def member(db_session, family):
    person = Person(
        first_name="Mario",
        last_name="Rossi",
        date_of_birth=date(1990, 1, 1),
        fingerprint_id="fp-001",
        family_id=family.id,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


def test_add_member(client, auth_headers, family):
    response = client.post(
        f"/api/families/{family.id}/members",
        headers=auth_headers,
        json={
            "first_name": "Luigi",
            "last_name": "Rossi",
            "date_of_birth": "1995-05-05",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Luigi"
    assert data["family_id"] == family.id
    assert data["fingerprint_id"] is None


def test_add_member_family_not_found(client, auth_headers):
    response = client.post(
        "/api/families/999/members",
        headers=auth_headers,
        json={
            "first_name": "Luigi",
            "last_name": "Rossi",
            "date_of_birth": "1995-05-05",
        },
    )
    assert response.status_code == 404


def test_add_member_duplicate_fingerprint(client, auth_headers, family, member):
    response = client.post(
        f"/api/families/{family.id}/members",
        headers=auth_headers,
        json={
            "first_name": "Luigi",
            "last_name": "Rossi",
            "date_of_birth": "1995-05-05",
            "fingerprint_id": "fp-001",
        },
    )
    assert response.status_code == 409


def test_update_member(client, auth_headers, member):
    response = client.put(
        f"/api/members/{member.id}",
        headers=auth_headers,
        json={"first_name": "Marco"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Marco"
    assert data["last_name"] == "Rossi"


def test_update_member_not_found(client, auth_headers):
    response = client.put(
        "/api/members/999",
        headers=auth_headers,
        json={"first_name": "Marco"},
    )
    assert response.status_code == 404


def test_update_member_keeps_own_fingerprint(client, auth_headers, member):
    response = client.put(
        f"/api/members/{member.id}",
        headers=auth_headers,
        json={"fingerprint_id": "fp-001"},
    )
    assert response.status_code == 200


def test_update_member_duplicate_fingerprint(
    client, auth_headers, db_session, family, member
):
    other = Person(
        first_name="Luigi",
        last_name="Rossi",
        date_of_birth=date(1995, 5, 5),
        fingerprint_id="fp-002",
        family_id=family.id,
    )
    db_session.add(other)
    db_session.commit()

    response = client.put(
        f"/api/members/{other.id}",
        headers=auth_headers,
        json={"fingerprint_id": "fp-001"},
    )
    assert response.status_code == 409


def test_delete_member(client, auth_headers, member, db_session):
    response = client.delete(f"/api/members/{member.id}", headers=auth_headers)
    assert response.status_code == 204
    assert db_session.get(Person, member.id) is None


def test_delete_member_not_found(client, auth_headers):
    response = client.delete("/api/members/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_member_with_distributions_blocked(
    client, auth_headers, db_session, family, member
):
    db_session.add(
        Distribution(
            family_id=family.id, person_id=member.id, package_type="standard"
        )
    )
    db_session.commit()

    response = client.delete(f"/api/members/{member.id}", headers=auth_headers)
    assert response.status_code == 409
    assert db_session.get(Person, member.id) is not None
