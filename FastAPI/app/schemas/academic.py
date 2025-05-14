# app/schemas/academic.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator


class SemesterBase(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True


class SemesterCreate(SemesterBase):
    pass


class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class Semester(SemesterBase):
    id: int

    class Config:
      model_config = { "from_attributes": True }


class SubjectBase(BaseModel):
    code: str
    name: str
    credits: int
    max_students: int


class SubjectCreate(SubjectBase):
    prerequisite_ids: Optional[List[int]] = []


class SubjectUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    credits: Optional[int] = None
    max_students: Optional[int] = None
    prerequisite_ids: Optional[List[int]] = None


class Subject(SubjectBase):
    id: int

    class Config:
        model_config = { "from_attributes": True }


class SubjectWithPrerequisites(Subject):
    prerequisites: List[Subject] = []


class ScheduleBase(BaseModel):
    subject_id: int
    teacher_id: int
    semester_id: int
    day_of_week: int
    start_time: str
    end_time: str
    classroom: str

    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if not 0 <= v <= 6:
            raise ValueError('day_of_week must be between 0 (Monday) and 6 (Sunday)')
        return v

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError('Time must be in format HH:MM')
        return v


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    classroom: Optional[str] = None


class Schedule(ScheduleBase):
    id: int

    class Config:
        model_config = { "from_attributes": True }


class ScheduleWithDetails(Schedule):
    subject: Subject
    teacher_name: str
    semester_name: str


class EnrollmentBase(BaseModel):
    student_id: int
    subject_id: int
    schedule_id: int
    semester_id: int


class EnrollmentCreate(EnrollmentBase):
    pass


class Enrollment(EnrollmentBase):
    id: int
    enrollment_date: datetime

    class Config:
        model_config = { "from_attributes": True }


class EnrollmentWithDetails(Enrollment):
    student_name: str
    subject_name: str
    schedule: Schedule


class GradeBase(BaseModel):
    enrollment_id: int
    evaluation_type: str
    weight: float
    score: float

    @validator('weight')
    def validate_weight(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Weight must be between 0.0 and 1.0')
        return v

    @validator('score')
    def validate_score(cls, v):
        if not 0 <= v <= 5:
            raise ValueError('Score must be between 0.0 and 5.0')
        return v


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    evaluation_type: Optional[str] = None
    weight: Optional[float] = None
    score: Optional[float] = None


class Grade(GradeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        model_config = { "from_attributes": True }


class AcademicRecord(BaseModel):
    student_id: int
    student_name: str
    cumulative_gpa: float
    total_credits: int
    semesters: List[dict]
