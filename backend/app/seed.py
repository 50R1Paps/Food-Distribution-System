"""Seed script: creates the initial admin user and sample package types.

Usage (from the backend/ directory):
    python -m app.seed [--username admin] [--password <password>]
"""

import argparse

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import PackageType, User
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed del database")
    parser.add_argument("--username", default="admin", help="Username dell'utente iniziale")
    parser.add_argument("--password", default="admin123", help="Password dell'utente iniziale")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        seed_user(db, args.username, args.password)
        seed_package_types(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
