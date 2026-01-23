from pydantic import BaseModel


class FeeResponse(BaseModel):
    id: str
    student_id: str
    amount: int
    due_date: str
    status: str
    payment_mode: str
    transaction_id: str | None = None

    model_config = {"from_attributes": True}


class FeeCreate(BaseModel):
    student_id: str
    amount: int
    due_date: str
    status: str = "pending"
    payment_mode: str = "online"


class FinancialKPIs(BaseModel):
    total_collected: int
    total_pending: int
    total_overdue: int
    collection_rate: float
    online_payments: int
    offline_payments: int
    average_fee_per_student: int


class FeeChartData(BaseModel):
    month: str
    online: int
    offline: int
    pending: int


class PaymentGatewayStatus(BaseModel):
    name: str
    status: str
    success_rate: float
    transactions: int
