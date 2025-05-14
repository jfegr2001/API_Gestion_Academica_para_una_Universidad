# app/routes/academic.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from core.database import get_db
from core.security import get_current_admin_user, get_current_user
from models.user import User, UserRole
from schemas.academic import (
    Semester, SemesterCreate, SemesterUpdate,
    Subject, SubjectCreate, SubjectUpdate, SubjectWithPrerequisites,
    Schedule, ScheduleCreate, ScheduleWithDetails,
    Enrollment, EnrollmentCreate, EnrollmentWithDetails,
    Grade, GradeCreate, GradeUpdate,
    AcademicRecord
)
from services.academic import (
    # Semester services
    create_semester, get_semester, get_semesters, get_active_semester,
    update_semester, delete_semester,
    
    # Subject services
    create_subject, get_subject, get_subjects, update_subject, delete_subject,
    
    # Schedule services
    create_schedule, get_schedule, get_schedules, delete_schedule,
    
    # Enrollment services
    create_enrollment, get_enrollment, get_enrollments, delete_enrollment,
    
    # Grade services
    create_grade, get_grade, get_grades, update_grade, delete_grade,
    
    # Academic record service
    get_student_academic_record
)

router = APIRouter(tags=["academic"])

# Semester endpoints
semester_router = APIRouter(prefix="/semesters", tags=["semesters"])

@semester_router.post("/", response_model=Semester)
def create_new_semester(
    semester: SemesterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return create_semester(db=db, semester=semester)


@semester_router.get("/", response_model=List[Semester])
def read_semesters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_semesters(db=db, skip=skip, limit=limit)


@semester_router.get("/active", response_model=Semester)
def read_active_semester(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    semester = get_active_semester(db=db)
    if not semester:
        raise HTTPException(status_code=404, detail="No active semester found")
    return semester


@semester_router.get("/{semester_id}", response_model=Semester)
def read_semester(
    semester_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    semester = get_semester(db=db, semester_id=semester_id)
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    return semester


@semester_router.put("/{semester_id}", response_model=Semester)
def update_semester_info(
    semester_id: int,
    semester: SemesterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return update_semester(db=db, semester_id=semester_id, semester=semester)


@semester_router.delete("/{semester_id}", response_model=Semester)
def delete_semester_record(
    semester_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return delete_semester(db=db, semester_id=semester_id)


# Subject endpoints
subject_router = APIRouter(prefix="/subjects", tags=["subjects"])

@subject_router.post("/", response_model=Subject)
def create_new_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return create_subject(db=db, subject=subject)


@subject_router.get("/", response_model=List[Subject])
def read_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_subjects(db=db, skip=skip, limit=limit)


@subject_router.get("/{subject_id}", response_model=SubjectWithPrerequisites)
def read_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = get_subject(db=db, subject_id=subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@subject_router.put("/{subject_id}", response_model=Subject)
def update_subject_info(
    subject_id: int,
    subject: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return update_subject(db=db, subject_id=subject_id, subject=subject)


@subject_router.delete("/{subject_id}", response_model=Subject)
def delete_subject_record(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return delete_subject(db=db, subject_id=subject_id)


# Schedule endpoints
schedule_router = APIRouter(prefix="/schedules", tags=["schedules"])

@schedule_router.post("/", response_model=Schedule)
def create_new_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return create_schedule(db=db, schedule=schedule)


@schedule_router.get("/", response_model=List[Schedule])
def read_schedules(
    skip: int = 0,
    limit: int = 100,
    semester_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_schedules(
        db=db, 
        skip=skip, 
        limit=limit, 
        semester_id=semester_id,
        subject_id=subject_id,
        teacher_id=teacher_id
    )


@schedule_router.get("/{schedule_id}", response_model=Schedule)
def read_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = get_schedule(db=db, schedule_id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@schedule_router.delete("/{schedule_id}", response_model=Schedule)
def delete_schedule_record(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return delete_schedule(db=db, schedule_id=schedule_id)


# Enrollment endpoints
enrollment_router = APIRouter(prefix="/enrollments", tags=["enrollments"])

@enrollment_router.post("/", response_model=Enrollment)
def create_new_enrollment(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Students can only enroll themselves
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only enroll themselves"
        )
    
    # Only admins and students can create enrollments
    if current_user.role == UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers cannot create enrollments"
        )
    
    return create_enrollment(db=db, enrollment=enrollment)


@enrollment_router.get("/", response_model=List[Enrollment])
def read_enrollments(
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Students can only see their own enrollments
    if current_user.role == UserRole.STUDENT:
        student_id = current_user.id
    
    return get_enrollments(
        db=db, 
        skip=skip, 
        limit=limit, 
        student_id=student_id,
        subject_id=subject_id,
        semester_id=semester_id
    )


@enrollment_router.get("/{enrollment_id}", response_model=Enrollment)
def read_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = get_enrollment(db=db, enrollment_id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Students can only see their own enrollments
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this enrollment"
        )
    
    return enrollment


@enrollment_router.delete("/{enrollment_id}", response_model=Enrollment)
def delete_enrollment_record(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = get_enrollment(db=db, enrollment_id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Students can only delete their own enrollments
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only delete their own enrollments"
        )
    
    # Teachers cannot delete enrollments
    if current_user.role == UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers cannot delete enrollments"
        )
    
    return delete_enrollment(db=db, enrollment_id=enrollment_id)


# Grade endpoints
grade_router = APIRouter(prefix="/grades", tags=["grades"])

@grade_router.post("/", response_model=Grade)
def create_new_grade(
    grade: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify if enrollment exists
    enrollment = get_enrollment(db=db, enrollment_id=grade.enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Get the schedule to verify the teacher
    schedule = get_schedule(db=db, schedule_id=enrollment.schedule_id)
    
    # Teachers can only grade their own classes
    if current_user.role == UserRole.TEACHER and schedule.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers can only grade their own classes"
        )
    
    # Students cannot create grades
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot create grades"
        )
    
    return create_grade(db=db, grade=grade)


@grade_router.get("/", response_model=List[Grade])
def read_grades(
    skip: int = 0,
    limit: int = 100,
    enrollment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If enrollment_id is provided, verify access permissions
    if enrollment_id:
        enrollment = get_enrollment(db=db, enrollment_id=enrollment_id)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        # Students can only see their own grades
        if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only see their own grades"
            )
        
        # Teachers can only see grades for their classes
        if current_user.role == UserRole.TEACHER:
            schedule = get_schedule(db=db, schedule_id=enrollment.schedule_id)
            if schedule.teacher_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Teachers can only see grades for their classes"
                )
    
    return get_grades(db=db, skip=skip, limit=limit, enrollment_id=enrollment_id)


@grade_router.get("/{grade_id}", response_model=Grade)
def read_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grade = get_grade(db=db, grade_id=grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    # Get enrollment to verify access permissions
    enrollment = get_enrollment(db=db, enrollment_id=grade.enrollment_id)
    
    # Students can only see their own grades
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only see their own grades"
        )
    
    # Teachers can only see grades for their classes
    if current_user.role == UserRole.TEACHER:
        schedule = get_schedule(db=db, schedule_id=enrollment.schedule_id)
        if schedule.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only see grades for their classes"
            )
    
    return grade


@grade_router.put("/{grade_id}", response_model=Grade)
def update_grade_info(
    grade_id: int,
    grade: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_grade = get_grade(db=db, grade_id=grade_id)
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    # Get enrollment to verify access permissions
    enrollment = get_enrollment(db=db, enrollment_id=db_grade.enrollment_id)
    
    # Students cannot update grades
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot update grades"
        )
    
    # Teachers can only update grades for their classes
    if current_user.role == UserRole.TEACHER:
        schedule = get_schedule(db=db, schedule_id=enrollment.schedule_id)
        if schedule.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only update grades for their classes"
            )
    
    return update_grade(db=db, grade_id=grade_id, grade=grade)


@grade_router.delete("/{grade_id}", response_model=Grade)
def delete_grade_record(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return delete_grade(db=db, grade_id=grade_id)


# Academic record endpoint
@router.get("/academic-record/{student_id}", response_model=AcademicRecord, tags=["academic-record"])
def get_academic_record(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Students can only see their own academic record
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only see their own academic record"
        )
    
    return get_student_academic_record(db=db, student_id=student_id)

