from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_users: int
    active_courses: int
    avg_attendance: float
    pending_tasks: int
    total_collected: int
    total_pending: int
    collection_rate: float
    online_percentage: float
    new_leads: int


class ChartDataPoint(BaseModel):
    label: str
    value: float


class EnrollmentData(BaseModel):
    month: str
    new_students: int
    dropouts: int


class AttendanceRateData(BaseModel):
    week: str
    rate: float
