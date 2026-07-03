from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class PackageTypeBase(BaseModel):
    name: str
    description: str | None = None
    cooldown_days: int = 30
    is_active: bool = True


class PackageTypeCreate(PackageTypeBase):
    pass


class PackageTypeOut(PackageTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FamilyBase(BaseModel):
    family_name: str
    address: str
    contact_number: str | None = None


class FamilyCreate(FamilyBase):
    pass


class FamilyOut(FamilyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class PersonBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    fingerprint_id: str | None = None
    family_id: int


class PersonCreate(PersonBase):
    pass


class PersonOut(PersonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class DistributionBase(BaseModel):
    family_id: int
    person_id: int
    package_type: str
    notes: str | None = None


class DistributionCreate(DistributionBase):
    pass


class DistributionOut(DistributionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    distribution_date: datetime
