from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    avatar: str | None = None
    department: str | None = None
    phone: str | None = None
    join_date: str | None = None
    roll_no: str | None = None
    specialization: str | None = None
    qualifications: str | None = None
    experience: str | None = None
    parent_name: str | None = None
    parent_phone: str | None = None
    cgpa: float | None = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    avatar: str | None = None
    department: str | None = None
    phone: str | None = None
    specialization: str | None = None
    qualifications: str | None = None
    experience: str | None = None
    parent_name: str | None = None
    parent_phone: str | None = None
    cgpa: float | None = None
