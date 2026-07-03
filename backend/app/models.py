from datetime import date, datetime, timezone

from sqlalchemy import Integer, String, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class PackageType(Base):
    __tablename__ = "package_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cooldown_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<PackageType {self.name}>"


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    members: Mapped[list["Person"]] = relationship("Person", back_populates="family")
    distributions: Mapped[list["Distribution"]] = relationship("Distribution", back_populates="family")

    def __repr__(self) -> str:
        return f"<Family {self.family_name}>"


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    fingerprint_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("families.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    family: Mapped["Family"] = relationship("Family", back_populates="members")
    distributions: Mapped[list["Distribution"]] = relationship("Distribution", back_populates="person")

    def __repr__(self) -> str:
        return f"<Person {self.first_name} {self.last_name}>"


class Distribution(Base):
    __tablename__ = "distributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("families.id"), nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"), nullable=False)
    package_type: Mapped[str] = mapped_column(String(50), nullable=False)
    distribution_date: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    family: Mapped["Family"] = relationship("Family", back_populates="distributions")
    person: Mapped["Person"] = relationship("Person", back_populates="distributions")

    def __repr__(self) -> str:
        return f"<Distribution {self.id}>"
