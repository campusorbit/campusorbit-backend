"""Schemas for all new ERP modules: Library, Documents, HR, Expenses, Exams, Calendar, Store, Vendors."""

from datetime import datetime

from pydantic import BaseModel


# ─── Library ───
class LibraryBookResponse(BaseModel):
    id: str
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int
    available_copies: int
    shelf_location: str
    publisher: str | None = None
    published_year: int | None = None
    barcode: str | None = None
    model_config = {"from_attributes": True}


class BookIssueResponse(BaseModel):
    id: str
    book_id: str
    student_id: str
    issue_date: str
    due_date: str
    return_date: str | None = None
    status: str
    fine: float = 0.0
    model_config = {"from_attributes": True}


class BookIssueCreate(BaseModel):
    book_id: str
    student_id: str
    issue_date: str
    due_date: str


# ─── Documents ───
class DocumentResponse(BaseModel):
    id: str
    title: str
    category: str
    file_type: str
    uploaded_by: str
    uploaded_date: str
    size: str
    description: str | None = None
    access_roles: str = "all"
    academic_year: str | None = None
    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    title: str
    category: str
    file_type: str
    uploaded_by: str
    uploaded_date: str
    size: str
    description: str | None = None
    access_roles: str = "all"
    academic_year: str | None = None


# ─── HR / Payroll ───
class SalarySlipResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    department: str
    designation: str
    month: str
    year: int
    basic: float
    hra: float = 0
    da: float = 0
    allowances: float = 0
    pf_deduction: float = 0
    tax_deduction: float = 0
    other_deductions: float = 0
    net_pay: float
    status: str
    paid_date: str | None = None
    model_config = {"from_attributes": True}


class LeaveRequestResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    leave_type: str
    start_date: str
    end_date: str
    days: int
    reason: str
    status: str
    approved_by: str | None = None
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


class LeaveRequestCreate(BaseModel):
    leave_type: str
    start_date: str
    end_date: str
    days: int
    reason: str


class LeaveRequestUpdate(BaseModel):
    status: str | None = None
    approved_by: str | None = None


# ─── Expenses & Budget ───
class ExpenseResponse(BaseModel):
    id: str
    title: str
    category: str
    amount: float
    date: str
    vendor: str | None = None
    approved_by: str | None = None
    status: str
    receipt_no: str | None = None
    notes: str | None = None
    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    title: str
    category: str
    amount: float
    date: str
    vendor: str | None = None
    receipt_no: str | None = None
    notes: str | None = None


class BudgetResponse(BaseModel):
    id: str
    category: str
    allocated: float
    spent: float
    academic_year: str
    model_config = {"from_attributes": True}


# ─── Exams ───
class ExamResponse(BaseModel):
    id: str
    title: str
    course_id: str
    course_name: str
    exam_type: str
    date: str
    duration_mins: int
    total_marks: int
    status: str
    instructions: str | None = None
    model_config = {"from_attributes": True}


class ExamCreate(BaseModel):
    title: str
    course_id: str
    course_name: str
    exam_type: str
    date: str
    duration_mins: int
    total_marks: int
    instructions: str | None = None


class ExamResultResponse(BaseModel):
    id: str
    exam_id: str
    student_id: str
    student_name: str
    marks_obtained: float
    total_marks: int
    percentage: float
    grade: str | None = None
    remarks: str | None = None
    model_config = {"from_attributes": True}


# ─── Calendar ───
class CalendarEventResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    event_type: str
    start_date: str
    end_date: str | None = None
    all_day: bool = True
    location: str | None = None
    color: str | None = None
    created_by: str | None = None
    model_config = {"from_attributes": True}


class CalendarEventCreate(BaseModel):
    title: str
    description: str | None = None
    event_type: str
    start_date: str
    end_date: str | None = None
    all_day: bool = True
    location: str | None = None
    color: str | None = None


# ─── Store ───
class StoreProductResponse(BaseModel):
    id: str
    name: str
    category: str
    price: float
    stock: int
    description: str | None = None
    image_url: str | None = None
    sku: str | None = None
    is_active: bool = True
    model_config = {"from_attributes": True}


class StoreOrderResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total: float
    status: str
    order_date: str
    model_config = {"from_attributes": True}


class StoreOrderCreate(BaseModel):
    product_id: str
    quantity: int


# ─── Vendors ───
class VendorResponse(BaseModel):
    id: str
    name: str
    contact_person: str
    email: str
    phone: str
    category: str
    address: str | None = None
    gst_no: str | None = None
    status: str
    contract_start: str | None = None
    contract_end: str | None = None
    rating: str | None = None
    model_config = {"from_attributes": True}


class VendorCreate(BaseModel):
    name: str
    contact_person: str
    email: str
    phone: str
    category: str
    address: str | None = None
    gst_no: str | None = None
    contract_start: str | None = None
    contract_end: str | None = None
