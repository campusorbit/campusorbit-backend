from datetime import datetime

from pydantic import BaseModel


class LeadResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    source: str
    status: str
    follow_up_date: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str
    source: str
    status: str = "interested"
    follow_up_date: str | None = None


class LeadUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    source: str | None = None
    status: str | None = None
    follow_up_date: str | None = None
