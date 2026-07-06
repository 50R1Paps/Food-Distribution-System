from datetime import date

import pytest

from app.models import Family, Person


@pytest.fixture()
def search_data(db_session):
    fam1 = Family(family_name="Rossi", address="Via Roma 1")
    fam2 = Family(family_name="Bianchi", address="Via Milano 2")
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
    p3 = Person(
        first_name="Anna", last_name="Verdi",
        date_of_birth=date(1995, 3, 20), family_id=fam1.id,
    )
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    return {"fam1": fam1, "fam2": fam2, "p1": p1, "p2": p2, "p3": p3}


def test_search_requires_auth(client):
    assert client.get("/api/search", params={"q": "test"}).status_code == 401


def test_search_requires_query_param(client, auth_headers):
    r = client.get("/api/search", headers=auth_headers)
    assert r.status_code == 422


def test_search_empty_query_rejected(client, auth_headers):
    r = client.get("/api/search", headers=auth_headers, params={"q": ""})
    assert r.status_code == 422


def test_search_families_by_name(client, auth_headers, search_data):
    r = client.get("/api/search", headers=auth_headers, params={"q": "ros"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    family_names = [f["family_name"] for f in data["families"]]
    assert "Rossi" in family_names
    assert "Bianchi" not in family_names


def test_search_persons_by_first_name(client, auth_headers, search_data):
    r = client.get("/api/search", headers=auth_headers, params={"q": "mar"})
    assert r.status_code == 200
    data = r.json()
    first_names = [p["first_name"] for p in data["persons"]]
    assert "Mario" in first_names


def test_search_persons_by_last_name(client, auth_headers, search_data):
    r = client.get("/api/search", headers=auth_headers, params={"q": "bianchi"})
    assert r.status_code == 200
    data = r.json()
    last_names = [p["last_name"] for p in data["persons"]]
    assert "Bianchi" in last_names


def test_search_returns_both_families_and_persons(client, auth_headers, search_data):
    r = client.get("/api/search", headers=auth_headers, params={"q": "rossi"})
    assert r.status_code == 200
    data = r.json()
    assert len(data["families"]) >= 1
    assert len(data["persons"]) >= 1
    assert data["total"] == len(data["families"]) + len(data["persons"])


def test_search_no_results(client, auth_headers, search_data):
    r = client.get("/api/search", headers=auth_headers, params={"q": "zzzzz"})
    assert r.status_code == 200
    data = r.json()
    assert data["families"] == []
    assert data["persons"] == []
    assert data["total"] == 0


def test_search_is_case_insensitive(client, auth_headers, search_data):
    r = client.get("/api/search", headers=auth_headers, params={"q": "ROSSI"})
    assert r.status_code == 200
    data = r.json()
    family_names = [f["family_name"] for f in data["families"]]
    assert "Rossi" in family_names


def test_search_pagination(client, auth_headers, db_session):
    for i in range(10):
        db_session.add(Family(family_name=f"FamTest{i}", address=f"Via {i}"))
    db_session.commit()

    r = client.get(
        "/api/search",
        headers=auth_headers,
        params={"q": "FamTest", "page": 1, "page_size": 5},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["families"]) <= 5


# --- SQL injection prevention ---


def test_search_sql_injection_single_quote(client, auth_headers, search_data):
    r = client.get(
        "/api/search",
        headers=auth_headers,
        params={"q": "' OR '1'='1"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["families"] == []
    assert data["persons"] == []


def test_search_sql_injection_union(client, auth_headers, search_data):
    r = client.get(
        "/api/search",
        headers=auth_headers,
        params={"q": "'; UNION SELECT * FROM users; --"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["families"] == []
    assert data["persons"] == []


def test_search_sql_injection_drop(client, auth_headers, search_data):
    r = client.get(
        "/api/search",
        headers=auth_headers,
        params={"q": "'; DROP TABLE families; --"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["families"] == []
    assert data["persons"] == []


def test_search_sql_injection_comment(client, auth_headers, search_data):
    r = client.get(
        "/api/search",
        headers=auth_headers,
        params={"q": "Rossi/*"},
    )
    assert r.status_code == 200
    data = r.json()
    family_names = [f["family_name"] for f in data["families"]]
    assert "Rossi" not in family_names


def test_search_sql_injection_semicolon(client, auth_headers, search_data):
    r = client.get(
        "/api/search",
        headers=auth_headers,
        params={"q": "Rossi;--"},
    )
    assert r.status_code == 200
    data = r.json()
    family_names = [f["family_name"] for f in data["families"]]
    assert "Rossi" not in family_names
