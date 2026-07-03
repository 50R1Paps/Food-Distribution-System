from datetime import date

import pytest

from app.models import Distribution, Family, Person


@pytest.fixture()
def family(db_session):
    fam = Family(family_name="Rossi", address="Via Roma 1", contact_number="123456")
    db_session.add(fam)
    db_session.commit()
    db_session.refresh(fam)
    return fam


def test_list_families_requires_auth(client):
    response = client.get("/api/families")
    assert response.status_code == 401


def test_list_families_empty(client, auth_headers):
    response = client.get("/api/families", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_create_family(client, auth_headers):
    response = client.post(
        "/api/families",
        headers=auth_headers,
        json={"family_name": "Bianchi", "address": "Via Milano 2"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["family_name"] == "Bianchi"
    assert data["address"] == "Via Milano 2"
    assert data["contact_number"] is None


def test_list_families_with_search(client, auth_headers, db_session, family):
    db_session.add(Family(family_name="Verdi", address="Via Napoli 3"))
    db_session.commit()

    response = client.get(
        "/api/families", headers=auth_headers, params={"search": "ros"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["family_name"] == "Rossi"


def test_list_families_pagination(client, auth_headers, db_session):
    for i in range(5):
        db_session.add(Family(family_name=f"Fam{i}", address=f"Via {i}"))
    db_session.commit()

    response = client.get(
        "/api/families",
        headers=auth_headers,
        params={"page": 2, "page_size": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 2


def test_get_family_detail(client, auth_headers, family):
    response = client.get(f"/api/families/{family.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["family_name"] == "Rossi"
    assert data["members"] == []
    assert data["distributions"] == []


def test_get_family_not_found(client, auth_headers):
    response = client.get("/api/families/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_family_partial(client, auth_headers, family):
    response = client.put(
        f"/api/families/{family.id}",
        headers=auth_headers,
        json={"address": "Via Nuova 10"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "Via Nuova 10"
    assert data["family_name"] == "Rossi"


def test_update_family_not_found(client, auth_headers):
    response = client.put(
        "/api/families/999",
        headers=auth_headers,
        json={"address": "Via Nuova 10"},
    )
    assert response.status_code == 404


def test_delete_family(client, auth_headers, family, db_session):
    response = client.delete(f"/api/families/{family.id}", headers=auth_headers)
    assert response.status_code == 204
    assert db_session.get(Family, family.id) is None


def test_delete_family_with_members_cascades(client, auth_headers, family, db_session):
    person = Person(
        first_name="Mario",
        last_name="Rossi",
        date_of_birth=date(1990, 1, 1),
        family_id=family.id,
    )
    db_session.add(person)
    db_session.commit()

    response = client.delete(f"/api/families/{family.id}", headers=auth_headers)
    assert response.status_code == 204
    assert db_session.get(Person, person.id) is None


def test_delete_family_with_distributions_blocked(
    client, auth_headers, family, db_session
):
    person = Person(
        first_name="Mario",
        last_name="Rossi",
        date_of_birth=date(1990, 1, 1),
        family_id=family.id,
    )
    db_session.add(person)
    db_session.commit()
    db_session.add(
        Distribution(
            family_id=family.id, person_id=person.id, package_type="standard"
        )
    )
    db_session.commit()

    response = client.delete(f"/api/families/{family.id}", headers=auth_headers)
    assert response.status_code == 409
    assert db_session.get(Family, family.id) is not None
