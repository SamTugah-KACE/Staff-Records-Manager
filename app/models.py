from sqlalchemy import Column, String, Boolean, JSON, Date, DateTime, Integer, ForeignKey, DECIMAL, CheckConstraint, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import validates, relationship, backref
from datetime import datetime, timedelta, timezone
from enum import Enum
import uuid
from database.db_session import Base
from sqlalchemy.dialects.postgresql import JSONB



# Enums
class MaritalStatus(Enum):
    Single = 'Single'
    Married = 'Married'
    Divorced = 'Divorced'
    Separated = 'Separated'
    Widowed = 'Widowed'
    Other = 'Other'

class Gender(Enum):
    Male = 'Male'
    Female = 'Female'
    Other = 'Other'

class Title(Enum):
    Prof = 'Prof.'
    Phd = 'PhD'
    Dr = 'Dr.'
    Mr = 'Mr.'
    Mrs = 'Mrs.'
    Ms = 'Ms.'
    Esq = 'Esq.'
    Hon = 'Hon.'
    Rev = 'Rev.'
    Msgr = 'Msgr.'
    Sr = 'Sr.'
    Other = 'Other'


# Calculate the range for the year constraint
current_year = datetime.now().year
min_year = current_year - 50


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class Centre(BaseModel):
    __tablename__ = "centre"

    location = Column(String, unique=True, nullable=False)
    region = Column(String, nullable=True)
    directorates = relationship('Directorate', backref='centre', cascade='all, delete-orphan')


class Directorate(BaseModel):
    __tablename__ = "directorate"

    name = Column(String,  unique=True, nullable=False)
    centre_id = Column(UUID(as_uuid=True), ForeignKey('centre.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    employment_details = relationship('EmploymentDetail', backref='directorate', cascade='all, delete-orphan')

    locale = relationship("Centre")


class Grade(BaseModel):
    __tablename__ = "grade"

    name = Column(String,  unique=True, nullable=False)
    min_sal = Column(DECIMAL(precision=10, scale=2), nullable=False,  default=0.00)
    max_sal = Column(DECIMAL(precision=10, scale=2), nullable=False,  default=0.00)
    employment_types = relationship('EmploymentType', backref='grade', cascade='all, delete-orphan')
    employment_details = relationship('EmploymentDetail', backref='grade', cascade='all, delete-orphan')


class EmploymentType(BaseModel):
    __tablename__ = "employment_type"

    name = Column(String,  unique=True, nullable=False)
    description = Column(String)
    grade_id = Column(UUID(as_uuid=True), ForeignKey('grade.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    employment_details = relationship('EmploymentDetail', backref='employment_type', cascade='all, delete-orphan')

    salary_grade = relationship("Grade")

class StaffCategory(BaseModel):
    __tablename__ = "staff_category"

    category = Column(String,  unique=True, nullable=False)
    employment_details = relationship('EmploymentDetail', backref='staff_category', cascade='all, delete-orphan')


class BioData(BaseModel):
    __tablename__ = "bio_data"

    title = Column(String, default=Title.Other.value, nullable=False)
    first_name = Column(String(100), nullable=False)
    other_names = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=False)
    previous_name = Column(String, nullable=True)
    gender = Column(String, default=Gender.Other.value, nullable=False)
    date_of_birth = Column(Date)
    nationality = Column(String)
    hometown = Column(String)
    religion = Column(String, nullable=True)
    marital_status = Column(String, default=MaritalStatus.Other.value, nullable=False)
    residential_addr = Column(String)
    active_phone_number = Column(String,  unique=True)
    email = Column(String, unique=True)
    ssnit_number = Column(String, unique=True)
    ghana_card_number = Column(String,  unique=True)
    is_physically_challenged = Column(Boolean)
    disability = Column(String, nullable=True)
    image_col = Column(String, unique=True, nullable=True)  #accept image file upload and store the file path to the copied directory
    registered_by = Column(String)
    extra_data = Column(JSONB, default={})  # For storing unknown/dynamic fields

    user = relationship('User', backref='bio_data', uselist=False, cascade='all, delete-orphan')
    employment_detail = relationship('EmploymentDetail', backref='bio_data', uselist=False, cascade='all, delete-orphan')
    bank_details = relationship('BankDetail', backref='bio_data', cascade='all, delete-orphan')
    academics = relationship('Academic', backref='bio_data', cascade='all, delete-orphan')
    professionals = relationship('Professional', backref='bio_data', cascade='all, delete-orphan')
    qualifications = relationship('Qualification', backref='bio_data', cascade='all, delete-orphan')
    employment_histories = relationship('EmploymentHistory', backref='bio_data', cascade='all, delete-orphan')
    family_infos = relationship('FamilyInfo', backref='bio_data', cascade='all, delete-orphan')
    emergency_contacts = relationship('EmergencyContact', backref='bio_data', cascade='all, delete-orphan')
    next_of_kins = relationship('NextOfKin', backref='bio_data', cascade='all, delete-orphan')
    declarations = relationship('Declaration', backref='bio_data', cascade='all, delete-orphan')


class User(BaseModel):
    __tablename__ = "users"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String,  unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    reset_pwd_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    lock_count = Column(Integer, default=0)

    bio_row = relationship("BioData")

    # def is_account_locked(self):
    #     if self.account_locked_until:
    #         print("datetime.now(): ", datetime.now(timezone.utc))
    #         return self.account_locked_until > datetime.now(timezone.utc)
    #     return False

    def is_account_locked(self):
        return self.account_locked_until and self.account_locked_until > datetime.now(timezone.utc)
    
    def lock_account(self, lock_time_minutes=10):
        self.account_locked_until = datetime.now(timezone.utc) + timedelta(minutes=lock_time_minutes)
        self.failed_login_attempts = 0  # Reset failed attempts after locking

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None


class RefreshToken(BaseModel):
        __tablename__ = "refresh_tokens"
        
        user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=True)
        refresh_token = Column(String, unique=True)
        expiration_time = Column(DateTime, nullable=False)

        user_token = relationship('User', backref='users', uselist=False)
     


class EmploymentDetail(BaseModel):
    __tablename__ = "employment_details"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    date_of_first_appointment = Column(Date, nullable=False)
    grade_on_first_appointment = Column(String, nullable=True)
    grade_on_current_appointment_id = Column(UUID(as_uuid=True), ForeignKey('grade.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    directorate_id = Column(UUID(as_uuid=True), ForeignKey('directorate.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    employee_number = Column(String, unique=True, index=True, nullable=False)
    employment_type_id = Column(UUID(as_uuid=True), ForeignKey('employment_type.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    staff_category_id = Column(UUID(as_uuid=True), ForeignKey('staff_category.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)

    bio_row = relationship("BioData")
    current_grade= relationship("Grade")
    department = relationship("Directorate")
    emp_type = relationship("EmploymentType")
    category=relationship("StaffCategory")



class BankDetail(BaseModel):
    __tablename__ = "bank_details"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    bank_name = Column(String, nullable=False)
    bank_branch = Column(String, nullable=False)
    account_number = Column(String, unique=True, nullable=False)
    account_type = Column(String, nullable=False)
    account_status = Column(String, nullable=True)

    bio_row = relationship("BioData")


class Academic(BaseModel):
    __tablename__ = "academics"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    institution = Column(String, nullable=False)
    year = Column(Date, CheckConstraint(f"year >= '{min_year}-01-01' AND year <= '{current_year}-12-31'"))
    programme = Column(String, nullable=True)
    qualification = Column(String, nullable=True)

    @validates('year')
    def validate_year(self, key, year):
        if year.year < min_year or year.year > current_year:
            raise ValueError(f"Year must be between {min_year} and {current_year}")
        return year

    bio_row = relationship("BioData")


class Professional(BaseModel):
    __tablename__ = "professional"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    year = Column(Date, CheckConstraint(f"year >= '{min_year}-01-01' AND year <= '{current_year}-12-31'"))
    certification = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    location = Column(String, nullable=True)

    @validates('year')
    def validate_year(self, key, year):
        if year.year < min_year or year.year > current_year:
            raise ValueError(f"Year must be between {min_year} and {current_year}")
        return year
    
    bio_row = relationship("BioData")


class Qualification(BaseModel):
    __tablename__ = "qualification"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    academic_qualification_id = Column(UUID(as_uuid=True), ForeignKey('academics.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    professional_qualification_id = Column(UUID(as_uuid=True), ForeignKey('professional.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    bio_row = relationship("BioData")
    academic_qualification = relationship("Academic")
    professional_qualification = relationship("Professional")


class EmploymentHistory(BaseModel):
    __tablename__ = "employment_history"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    date_employed = Column(Date, nullable=False)
    institution = Column(String, nullable=False)
    position = Column(String, nullable=False)
    end_date = Column(Date)

    bio_row = relationship("BioData")


class FamilyInfo(BaseModel):
    __tablename__ = "family_info"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name_of_spouse = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    phone_number = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)
    name_of_father_guardian = Column(String, nullable=True)
    fathers_occupation = Column(String, nullable=True)
    fathers_contact = Column(String, nullable=True)
    fathers_address = Column(String, nullable=True)
    name_of_mother_guardian = Column(String, nullable=True)
    mothers_occupation = Column(String, nullable=True)
    mothers_contact = Column(String, nullable=True)
    mothers_address = Column(String, nullable=True)
    children_name = Column(String, nullable=True)
    children_dob = Column(String, nullable=True)

    bio_row = relationship("BioData")


class EmergencyContact(BaseModel):
    __tablename__ = "emergency_contacts"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = Column(String)
    phone_number = Column(String, unique=True)
    address = Column(String)
    email = Column(String)

    bio_row = relationship("BioData")


class NextOfKin(BaseModel):
    __tablename__ = "next_of_kin"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    title = Column(String, default=Title.Other.value, nullable=False)
    first_name = Column(String(100), nullable=False)
    other_name = Column(String(100))
    surname = Column(String(100), nullable=False)
    gender = Column(String, default=Gender.Other.value, nullable=False)
    relation = Column(String, nullable=False)
    address = Column(String)
    town = Column(String, nullable=False)
    region = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    bio_row = relationship("BioData")


class Declaration(BaseModel):
    __tablename__ = "declaration"

    bio_row_id = Column(UUID(as_uuid=True), ForeignKey('bio_data.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    status = Column(Boolean, default=False)
    reps_signature = Column(String, unique=True,nullable=True)  #accept image file upload (supervisor's signature image) and store the file path to the copied directory
    employees_signature = Column(String, unique=True, nullable=True) #accept image file upload (employee's signature image) and store the file path to the copied directory
    declaration_date = Column(Date, default=func.now())

    bio_row = relationship("BioData")

class Trademark(BaseModel):
    __tablename__ = "trademark"

    name = Column(String, unique=True, nullable=False)
    left_logo = Column(String, nullable=True) #accept image file upload and store the file path to the copied directory
    right_logo = Column(String, nullable=True) #accept image file upload and store the file path to the copied directory


class UserRole(BaseModel):
    __tablename__ = "user_role"

    roles = Column(String, unique=True, nullable=False)
    dashboard = Column(String)

    
class SavedForm(BaseModel):
    __tablename__ = "saved_forms"

    form_layout = Column(JSON, nullable=False)  # Store form layout as JSON
