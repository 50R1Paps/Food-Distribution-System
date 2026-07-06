"""Seed script: creates the initial admin user, sample package types, and demo data.

Usage (from the backend/ directory):
    python -m app.seed [--username admin] [--password <password>] [--demo]
"""

import argparse
from datetime import date, datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Distribution, Family, PackageType, Person, User
from app.security import hash_password

SAMPLE_PACKAGE_TYPES = [
    {
        "name": "Pacco alimentare standard",
        "description": "Pacco alimentare di base con generi di prima necessità",
        "cooldown_days": 30,
    },
    {
        "name": "Pacco freschi",
        "description": "Prodotti freschi: frutta, verdura e latticini",
        "cooldown_days": 7,
    },
    {
        "name": "Pacco igiene",
        "description": "Prodotti per l'igiene personale e della casa",
        "cooldown_days": 60,
    },
]


def seed_user(db: Session, username: str, password: str) -> None:
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"Utente '{username}' già esistente, salto.")
        return
    db.add(User(username=username, hashed_password=hash_password(password)))
    db.commit()
    print(f"Utente '{username}' creato.")


def seed_package_types(db: Session) -> None:
    for data in SAMPLE_PACKAGE_TYPES:
        existing = db.query(PackageType).filter(PackageType.name == data["name"]).first()
        if existing:
            print(f"Tipo pacco '{data['name']}' già esistente, salto.")
            continue
        db.add(PackageType(**data))
        print(f"Tipo pacco '{data['name']}' creato.")
    db.commit()


SAMPLE_FAMILIES = [
    {
        "family_name": "Rossi",
        "address": "Via Garibaldi 12, Milano",
        "contact_number": "+39 333 1234567",
        "members": [
            {"first_name": "Marco", "last_name": "Rossi", "date_of_birth": date(1985, 3, 15)},
            {"first_name": "Laura", "last_name": "Rossi", "date_of_birth": date(1988, 7, 22)},
            {"first_name": "Giulia", "last_name": "Rossi", "date_of_birth": date(2015, 1, 10)},
        ],
    },
    {
        "family_name": "Bianchi",
        "address": "Via Roma 45, Roma",
        "contact_number": "+39 340 9876543",
        "members": [
            {"first_name": "Luca", "last_name": "Bianchi", "date_of_birth": date(1990, 11, 5)},
            {"first_name": "Anna", "last_name": "Bianchi", "date_of_birth": date(1992, 9, 18)},
        ],
    },
    {
        "family_name": "Esposito",
        "address": "Corso Vittorio Emanuele 78, Napoli",
        "contact_number": "+39 320 5551234",
        "members": [
            {"first_name": "Giuseppe", "last_name": "Esposito", "date_of_birth": date(1978, 6, 30)},
            {"first_name": "Maria", "last_name": "Esposito", "date_of_birth": date(1980, 12, 3)},
            {"first_name": "Francesco", "last_name": "Esposito", "date_of_birth": date(2010, 5, 14)},
            {"first_name": "Sofia", "last_name": "Esposito", "date_of_birth": date(2012, 8, 25)},
        ],
    },
    {
        "family_name": "Conti",
        "address": "Via Dante 3, Firenze",
        "contact_number": None,
        "members": [
            {"first_name": "Paolo", "last_name": "Conti", "date_of_birth": date(1995, 2, 28)},
        ],
    },
    {
        "family_name": "Romano",
        "address": "Piazza del Popolo 9, Bologna",
        "contact_number": "+39 348 2223344",
        "members": [
            {"first_name": "Elena", "last_name": "Romano", "date_of_birth": date(1983, 4, 12)},
            {"first_name": "Davide", "last_name": "Romano", "date_of_birth": date(1981, 10, 7)},
            {"first_name": "Marta", "last_name": "Romano", "date_of_birth": date(2018, 3, 20)},
        ],
    },
]


def seed_demo(db: Session) -> None:
    if db.query(Family).count() > 0:
        print("Famiglie già presenti, salto il seed demo.")
        return

    package_types = db.query(PackageType).all()
    pt_names = {pt.name: pt for pt in package_types}

    now = datetime.now(timezone.utc)

    for fam_data in SAMPLE_FAMILIES:
        members_data = fam_data.pop("members")
        family = Family(**fam_data)
        db.add(family)
        db.flush()

        persons = []
        for m in members_data:
            person = Person(family_id=family.id, **m)
            db.add(person)
            persons.append(person)

        db.flush()

        # Crea 1-3 distribuzioni per le prime 3 famiglie
        if family.id <= 3:
            pt = package_types[(family.id - 1) % len(package_types)]
            dist1 = Distribution(
                family_id=family.id,
                person_id=persons[0].id,
                package_type=pt.name,
                distribution_date=now - timedelta(days=45),
                notes="Prima distribuzione",
                is_emergency=False,
            )
            db.add(dist1)

            if len(persons) > 1:
                pt2 = package_types[family.id % len(package_types)]
                dist2 = Distribution(
                    family_id=family.id,
                    person_id=persons[1].id,
                    package_type=pt2.name,
                    distribution_date=now - timedelta(days=10),
                    notes="Distribuzione regolare",
                    is_emergency=False,
                )
                db.add(dist2)

            # Una distribuzione di emergenza per la famiglia 2
            if family.id == 2:
                dist3 = Distribution(
                    family_id=family.id,
                    person_id=persons[0].id,
                    package_type=package_types[0].name,
                    distribution_date=now - timedelta(days=2),
                    notes="Emergenza: necessità immediata",
                    is_emergency=True,
                )
                db.add(dist3)

    db.commit()
    print(f"Create {db.query(Family).count()} famiglie, "
          f"{db.query(Person).count()} persone, "
          f"{db.query(Distribution).count()} distribuzioni.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed del database")
    parser.add_argument("--username", default="admin", help="Username dell'utente iniziale")
    parser.add_argument("--password", default="admin123", help="Password dell'utente iniziale")
    parser.add_argument("--demo", action="store_true", help="Popola anche con dati dimostrativi")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        seed_user(db, args.username, args.password)
        seed_package_types(db)
        if args.demo:
            seed_demo(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
