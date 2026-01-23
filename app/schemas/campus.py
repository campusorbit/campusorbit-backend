from datetime import datetime

from pydantic import BaseModel


class CampusNewsResponse(BaseModel):
    id: str
    title: str
    content: str
    date: str
    category: str
    author: str

    model_config = {"from_attributes": True}


class CampusNewsCreate(BaseModel):
    title: str
    content: str
    date: str
    category: str
    author: str


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    message: str
    read: bool = False
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class InventoryResponse(BaseModel):
    id: str
    name: str
    category: str
    quantity: int
    location: str
    condition: str
    last_updated: str

    model_config = {"from_attributes": True}


class InventoryCreate(BaseModel):
    name: str
    category: str
    quantity: int
    location: str
    condition: str
    last_updated: str


class TransportBusResponse(BaseModel):
    id: str
    bus_no: str
    route: str
    latitude: float
    longitude: float
    speed: float = 0
    student_count: int = 0

    model_config = {"from_attributes": True}


class TransportBusUpdate(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    speed: float | None = None
    student_count: int | None = None


class PricingPlanResponse(BaseModel):
    id: str
    name: str
    price: int
    features: list[str]
    icon: str
    highlighted: bool = False

    model_config = {"from_attributes": True}


class MarketplaceResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    icon: str

    model_config = {"from_attributes": True}


class SubstitutionResponse(BaseModel):
    id: str
    date: str
    time: str
    course: str
    original_teacher: str
    reason: str
    status: str
    assigned_teacher: str | None = None
    suggested_teachers: list[str] | None = None

    model_config = {"from_attributes": True}


class SubstitutionCreate(BaseModel):
    date: str
    time: str
    course: str
    original_teacher: str
    reason: str
    suggested_teachers: list[str] | None = None


class SubstitutionUpdate(BaseModel):
    status: str | None = None
    assigned_teacher: str | None = None


class ComplaintResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    description: str
    category: str
    status: str
    priority: str
    resolution: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ComplaintCreate(BaseModel):
    subject: str
    description: str
    category: str
    priority: str = "medium"


class ComplaintUpdate(BaseModel):
    status: str | None = None
    resolution: str | None = None
    priority: str | None = None
