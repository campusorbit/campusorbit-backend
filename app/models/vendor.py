from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # IT, Maintenance, Catering, Transport, Stationery
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    gst_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")  # active, inactive
    contract_start: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contract_end: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rating: Mapped[str | None] = mapped_column(String(5), nullable=True)  # 1-5
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
