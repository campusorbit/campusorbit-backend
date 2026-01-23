from pydantic import BaseModel


class CourseResponse(BaseModel):
    id: str
    code: str
    name: str
    instructor_id: str
    semester: str
    credits: int
    description: str | None = None
    student_count: int = 0
    instructor_name: str | None = None

    model_config = {"from_attributes": True}


class CourseCreate(BaseModel):
    code: str
    name: str
    instructor_id: str
    semester: str
    credits: int
    description: str | None = None
    student_count: int = 0


class AssignmentResponse(BaseModel):
    id: str
    course_id: str
    title: str
    description: str | None = None
    due_date: str
    submitted_by: int = 0
    total_students: int = 0

    model_config = {"from_attributes": True}


class AssignmentCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: str
    total_students: int = 0


class GradeResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    midterm: float | None = None
    endterm: float | None = None
    assignment_score: float | None = None
    grade_letter: str | None = None

    model_config = {"from_attributes": True}


class GradeCreate(BaseModel):
    student_id: str
    midterm: float | None = None
    endterm: float | None = None
    assignment_score: float | None = None
    grade_letter: str | None = None


class StudyMaterialResponse(BaseModel):
    id: str
    course_id: str
    title: str
    type: str
    uploaded_date: str
    size: str
    downloads: int = 0

    model_config = {"from_attributes": True}


class StudyMaterialCreate(BaseModel):
    title: str
    type: str
    uploaded_date: str
    size: str


class SyllabusResponse(BaseModel):
    id: str
    course_id: str
    unit_number: int
    title: str
    topics: str
    hours: int = 0

    model_config = {"from_attributes": True}


class SyllabusCreate(BaseModel):
    unit_number: int
    title: str
    topics: str
    hours: int = 0
