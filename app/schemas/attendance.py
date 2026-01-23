from pydantic import BaseModel


class AttendanceResponse(BaseModel):
    id: str
    student_id: str
    date: str
    status: str

    model_config = {"from_attributes": True}


class AttendanceCreate(BaseModel):
    student_id: str
    date: str
    status: str


class BiometricRecordResponse(BaseModel):
    id: str
    teacher_id: str
    date: str
    check_in: str
    check_out: str | None = None
    hours_worked: float = 0

    model_config = {"from_attributes": True}


class BiometricRecordCreate(BaseModel):
    teacher_id: str
    date: str
    check_in: str
    check_out: str | None = None
    hours_worked: float = 0


class AttendanceReport(BaseModel):
    total_days: int
    present: int
    absent: int
    late: int
    percentage: float
