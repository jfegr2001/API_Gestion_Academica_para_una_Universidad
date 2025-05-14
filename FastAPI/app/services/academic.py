# app/services/academic.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.academic import Semester, Subject, Schedule, Enrollment, Grade
from models.user import User, UserRole
from schemas.academic import (
    SemesterCreate, SemesterUpdate,
    SubjectCreate, SubjectUpdate,
    ScheduleCreate,
    EnrollmentCreate,
    GradeCreate, GradeUpdate
)


# Semester Services
def create_semester(db: Session, semester: SemesterCreate) -> Semester:
    db_semester = Semester(
        name=semester.name,
        start_date=semester.start_date,
        end_date=semester.end_date,
        is_active=semester.is_active
    )
    db.add(db_semester)
    db.commit()
    db.refresh(db_semester)
    return db_semester


def get_semester(db: Session, semester_id: int) -> Optional[Semester]:
    return db.query(Semester).filter(Semester.id == semester_id).first()


def get_semesters(db: Session, skip: int = 0, limit: int = 100) -> List[Semester]:
    return db.query(Semester).offset(skip).limit(limit).all()


def get_active_semester(db: Session) -> Optional[Semester]:
    return db.query(Semester).filter(Semester.is_active == True).first()


def update_semester(db: Session, semester_id: int, semester: SemesterUpdate) -> Semester:
    db_semester = get_semester(db, semester_id)
    if not db_semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found"
        )
    
    update_data = semester.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_semester, field, value)
    
    db.commit()
    db.refresh(db_semester)
    return db_semester


def delete_semester(db: Session, semester_id: int) -> Semester:
    db_semester = get_semester(db, semester_id)
    if not db_semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found"
        )
    
    # Verificar si hay matrículas asociadas
    enrollments_count = db.query(Enrollment).filter(Enrollment.semester_id == semester_id).count()
    if enrollments_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete semester with {enrollments_count} enrollments"
        )
    
    db.delete(db_semester)
    db.commit()
    return db_semester


# Subject Services
def create_subject(db: Session, subject: SubjectCreate) -> Subject:
    db_subject = Subject(
        code=subject.code,
        name=subject.name,
        credits=subject.credits,
        max_students=subject.max_students
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    
    # Add prerequisites if any
    if subject.prerequisite_ids:
        for prereq_id in subject.prerequisite_ids:
            prereq = db.query(Subject).filter(Subject.id == prereq_id).first()
            if prereq:
                db_subject.prerequisites.append(prereq)
        db.commit()
        db.refresh(db_subject)
    
    return db_subject


def get_subject(db: Session, subject_id: int) -> Optional[Subject]:
    return db.query(Subject).filter(Subject.id == subject_id).first()


def get_subject_by_code(db: Session, code: str) -> Optional[Subject]:
    return db.query(Subject).filter(Subject.code == code).first()


def get_subjects(db: Session, skip: int = 0, limit: int = 100) -> List[Subject]:
    return db.query(Subject).offset(skip).limit(limit).all()


def update_subject(db: Session, subject_id: int, subject: SubjectUpdate) -> Subject:
    db_subject = get_subject(db, subject_id)
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    update_data = subject.dict(exclude_unset=True, exclude={"prerequisite_ids"})
    for field, value in update_data.items():
        setattr(db_subject, field, value)
    
    # Update prerequisites if specified
    if subject.prerequisite_ids is not None:
        # Clear existing prerequisites
        db_subject.prerequisites.clear()
        
        # Add new prerequisites
        for prereq_id in subject.prerequisite_ids:
            prereq = db.query(Subject).filter(Subject.id == prereq_id).first()
            if prereq:
                db_subject.prerequisites.append(prereq)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: int) -> Subject:
    db_subject = get_subject(db, subject_id)
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Check if subject has enrollments
    enrollments_count = db.query(Enrollment).filter(Enrollment.subject_id == subject_id).count()
    if enrollments_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete subject with {enrollments_count} enrollments"
        )
    
    # Remove subject from prerequisites
    db_subject.prerequisites.clear()
    
    db.delete(db_subject)
    db.commit()
    return db_subject


# Schedule Services
def create_schedule(db: Session, schedule: ScheduleCreate) -> Schedule:
    # Validate subject exists
    subject = db.query(Subject).filter(Subject.id == schedule.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Validate teacher exists and is a teacher
    teacher = db.query(User).filter(
        User.id == schedule.teacher_id, 
        User.role == UserRole.TEACHER
    ).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    # Validate semester exists
    semester = db.query(Semester).filter(Semester.id == schedule.semester_id).first()
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found"
        )
    
    # Check for classroom conflicts
    classroom_conflict = db.query(Schedule).filter(
        Schedule.classroom == schedule.classroom,
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.semester_id == schedule.semester_id,
        Schedule.start_time <= schedule.end_time,
        Schedule.end_time >= schedule.start_time
    ).first()
    
    if classroom_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Classroom {schedule.classroom} is already booked at that time"
        )
    
    # Check for teacher conflicts
    teacher_conflict = db.query(Schedule).filter(
        Schedule.teacher_id == schedule.teacher_id,
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.semester_id == schedule.semester_id,
        Schedule.start_time <= schedule.end_time,
        Schedule.end_time >= schedule.start_time
    ).first()
    
    if teacher_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher has another class at that time"
        )
    
    db_schedule = Schedule(
        subject_id=schedule.subject_id,
        teacher_id=schedule.teacher_id,
        semester_id=schedule.semester_id,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        classroom=schedule.classroom
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_schedule(db: Session, schedule_id: int) -> Optional[Schedule]:
    return db.query(Schedule).filter(Schedule.id == schedule_id).first()


def get_schedules(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    semester_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    teacher_id: Optional[int] = None
) -> List[Schedule]:
    query = db.query(Schedule)
    
    if semester_id:
        query = query.filter(Schedule.semester_id == semester_id)
    if subject_id:
        query = query.filter(Schedule.subject_id == subject_id)
    if teacher_id:
        query = query.filter(Schedule.teacher_id == teacher_id)
        
    return query.offset(skip).limit(limit).all()


def delete_schedule(db: Session, schedule_id: int) -> Schedule:
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Check for enrollments in this schedule
    enrollments_count = db.query(Enrollment).filter(Enrollment.schedule_id == schedule_id).count()
    if enrollments_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete schedule with {enrollments_count} enrollments"
        )
    
    db.delete(db_schedule)
    db.commit()
    return db_schedule


# Enrollment Services
def create_enrollment(db: Session, enrollment: EnrollmentCreate) -> Enrollment:
    # Validate student exists and is a student
    student = db.query(User).filter(
        User.id == enrollment.student_id,
        User.role == UserRole.STUDENT
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Validate subject exists
    subject = db.query(Subject).filter(Subject.id == enrollment.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Validate schedule exists and matches the subject
    schedule = db.query(Schedule).filter(
        Schedule.id == enrollment.schedule_id,
        Schedule.subject_id == enrollment.subject_id
    ).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found or does not match subject"
        )
    
    # Validate semester exists
    semester = db.query(Semester).filter(
        Semester.id == enrollment.semester_id,
        Semester.is_active == True
    ).first()
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active semester not found"
        )
    
    # Check if student is already enrolled in this subject for this semester
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.subject_id == enrollment.subject_id,
        Enrollment.semester_id == enrollment.semester_id
    ).first()
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this subject for this semester"
        )
    
    # Check for schedule conflicts
    student_schedules = db.query(Schedule).join(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.semester_id == enrollment.semester_id,
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.start_time <= schedule.end_time,
        Schedule.end_time >= schedule.start_time
    ).all()
    
    if student_schedules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student has a schedule conflict"
        )
    
    # Check subject capacity
    current_enrollments = db.query(Enrollment).filter(
        Enrollment.subject_id == enrollment.subject_id,
        Enrollment.semester_id == enrollment.semester_id,
        Enrollment.schedule_id == enrollment.schedule_id
    ).count()
    
    if current_enrollments >= subject.max_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject has reached maximum capacity"
        )
    
    # Check prerequisites
    if subject.prerequisites:
        for prereq in subject.prerequisites:
            # Check if student has passed the prerequisite
            passed_prereq = db.query(Enrollment).join(Grade).filter(
                Enrollment.student_id == enrollment.student_id,
                Enrollment.subject_id == prereq.id,
                Grade.evaluation_type == "final",
                Grade.score >= 3.0  # Assuming 3.0 is the passing grade
            ).first()
            
            if not passed_prereq:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Student has not passed prerequisite: {prereq.name}"
                )
    
    db_enrollment = Enrollment(
        student_id=enrollment.student_id,
        subject_id=enrollment.subject_id,
        schedule_id=enrollment.schedule_id,
        semester_id=enrollment.semester_id,
        enrollment_date=datetime.utcnow()
    )
    
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment


def get_enrollment(db: Session, enrollment_id: int) -> Optional[Enrollment]:
    return db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()


def get_enrollments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    semester_id: Optional[int] = None
) -> List[Enrollment]:
    query = db.query(Enrollment)
    
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
    if subject_id:
        query = query.filter(Enrollment.subject_id == subject_id)
    if semester_id:
        query = query.filter(Enrollment.semester_id == semester_id)
        
    return query.offset(skip).limit(limit).all()


def delete_enrollment(db: Session, enrollment_id: int) -> Enrollment:
    db_enrollment = get_enrollment(db, enrollment_id)
    if not db_enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check if there are any grades
    grades_count = db.query(Grade).filter(Grade.enrollment_id == enrollment_id).count()
    if grades_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete enrollment with {grades_count} grades"
        )
    
    db.delete(db_enrollment)
    db.commit()
    return db_enrollment


# Grade Services
def create_grade(db: Session, grade: GradeCreate) -> Grade:
    # Validate enrollment exists
    enrollment = db.query(Enrollment).filter(Enrollment.id == grade.enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check if a grade for this evaluation type already exists
    existing_grade = db.query(Grade).filter(
        Grade.enrollment_id == grade.enrollment_id,
        Grade.evaluation_type == grade.evaluation_type
    ).first()
    
    if existing_grade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A grade for {grade.evaluation_type} already exists"
        )
    
    db_grade = Grade(
        enrollment_id=grade.enrollment_id,
        evaluation_type=grade.evaluation_type,
        weight=grade.weight,
        score=grade.score
    )
    
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade


def get_grade(db: Session, grade_id: int) -> Optional[Grade]:
    return db.query(Grade).filter(Grade.id == grade_id).first()


def get_grades(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    enrollment_id: Optional[int] = None
) -> List[Grade]:
    query = db.query(Grade)
    
    if enrollment_id:
        query = query.filter(Grade.enrollment_id == enrollment_id)
        
    return query.offset(skip).limit(limit).all()


def update_grade(db: Session, grade_id: int, grade: GradeUpdate) -> Grade:
    db_grade = get_grade(db, grade_id)
    if not db_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    update_data = grade.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_grade, field, value)
    
    db_grade.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_grade)
    return db_grade


def delete_grade(db: Session, grade_id: int) -> Grade:
    db_grade = get_grade(db, grade_id)
    if not db_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    db.delete(db_grade)
    db.commit()
    return db_grade


# Academic Record Services
def get_student_academic_record(db: Session, student_id: int) -> Dict[str, Any]:
    # Verificar que el estudiante existe
    student = db.query(User).filter(
        User.id == student_id,
        User.role == UserRole.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Obtener todas las matrículas del estudiante
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id
    ).all()
    
    if not enrollments:
        return {
            "student_id": student_id,
            "student_name": student.full_name,
            "cumulative_gpa": 0.0,
            "total_credits": 0,
            "semesters": []
        }
    
    # Inicializar datos del historial académico
    semesters_data = {}
    total_grade_points = 0
    total_credits = 0
    
    # Procesar cada matrícula
    for enrollment in enrollments:
        semester = db.query(Semester).filter(Semester.id == enrollment.semester_id).first()
        subject = db.query(Subject).filter(Subject.id == enrollment.subject_id).first()
        grades = db.query(Grade).filter(Grade.enrollment_id == enrollment.id).all()
        
        # Calcular la nota final para esta matrícula
        final_score = 0
        for grade in grades:
            final_score += grade.score * grade.weight
        
        # Si no hay semestre en el diccionario, agregarlo
        if semester.id not in semesters_data:
            semesters_data[semester.id] = {
                "semester_name": semester.name,
                "start_date": semester.start_date,
                "end_date": semester.end_date,
                "subjects": [],
                "semester_gpa": 0,
                "semester_credits": 0
            }
        
        # Agregar información de la asignatura
        semesters_data[semester.id]["subjects"].append({
            "subject_code": subject.code,
            "subject_name": subject.name,
            "credits": subject.credits,
            "final_score": round(final_score, 2),
            "passed": final_score >= 3.0  # Assuming 3.0 is passing grade
        })
        
        # Actualizar créditos y puntos para GPA del semestre
        semesters_data[semester.id]["semester_credits"] += subject.credits
        semesters_data[semester.id]["semester_gpa"] += final_score * subject.credits
        
        # Actualizar acumulados si la materia fue aprobada
        if final_score >= 3.0:
            total_grade_points += final_score * subject.credits
            total_credits += subject.credits
    
    # Calcular GPA para cada semestre
    for semester_id in semesters_data:
        if semesters_data[semester_id]["semester_credits"] > 0:
            semesters_data[semester_id]["semester_gpa"] /= semesters_data[semester_id]["semester_credits"]
            semesters_data[semester_id]["semester_gpa"] = round(semesters_data[semester_id]["semester_gpa"], 2)
    
    # Calcular GPA acumulado
    cumulative_gpa = 0
    if total_credits > 0:
        cumulative_gpa = round(total_grade_points / total_credits, 2)
    
    # Ordenar los semestres por fecha
    sorted_semesters = sorted(
        semesters_data.values(),
        key=lambda x: x["start_date"]
    )
    
    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "cumulative_gpa": cumulative_gpa,
        "total_credits": total_credits,
        "semesters": sorted_semesters
    }
