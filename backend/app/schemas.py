from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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


class PackageTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cooldown_days: int | None = None
    is_active: bool | None = None


class PackageTypeOut(PackageTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FamilyBase(BaseModel):
    family_name: str
    address: str
    contact_number: str | None = None


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(BaseModel):
    family_name: str | None = None
    address: str | None = None
    contact_number: str | None = None


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


class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    fingerprint_id: str | None = None


class PersonUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    fingerprint_id: str | None = None


class PersonOut(PersonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class DistributionBase(BaseModel):
    family_id: int
    person_id: int
    package_type: str
    notes: str | None = None


class DistributionCreate(BaseModel):
    person_id: int | None = None
    fingerprint_id: str | None = None
    package_type_id: int
    notes: str | None = None
    is_emergency: bool = False


class DistributionOut(DistributionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    distribution_date: datetime
    is_emergency: bool = False


class CooldownWarning(BaseModel):
    warning: str
    last_distribution_date: datetime
    cooldown_days: int
    next_allowed_date: datetime


class DistributionReceipt(DistributionOut):
    family_name: str
    person_name: str


class DistributionPage(BaseModel):
    items: list[DistributionReceipt]
    total: int
    page: int
    page_size: int


class FamilyDetail(FamilyOut):
    members: list[PersonOut] = []
    distributions: list[DistributionOut] = []


class FamilyPage(BaseModel):
    items: list[FamilyOut]
    total: int
    page: int
    page_size: int
