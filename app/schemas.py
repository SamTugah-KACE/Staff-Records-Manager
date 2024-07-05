from pydantic import BaseModel, EmailStr, condecimal,  constr, validator, Field, UUID4
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
import uuid
from decimal import Decimal
from re import Pattern
from uuid import UUID


# Enums
class MaritalStatus(str, Enum):
    Single = 'Single'
    Married = 'Married'
    Divorced = 'Divorced'
    Separated = 'Separated'
    Widowed = 'Widowed'
    Other = 'Other'

class Gender(str, Enum):
    Male = 'Male'
    Female = 'Female'
    Other = 'Other'

class Title(str, Enum):
    Prof = 'Prof.'
    Dr = 'Dr.'
    Mr = 'Mr.'
    Mrs = 'Mrs.'
    Ms = 'Ms.'
    Other = 'Other'


class BaseSchema(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True




# Phone number validator
def phone_number_validator(v: str) -> str:
    if len(v) > 18 or not v.replace(" ", "").replace("+", "").isdigit() or "  " in v:
        raise ValueError('Invalid phone number format')
    return v

# Common fields
class NameFieldsMixin(BaseModel):
    first_name: str =constr(max_length=100)
    other_names: str = Optional[constr(max_length=100)]
    surname: str = constr(max_length=100)
    previous_name: Optional[str]

class ContactFieldsMixin(BaseModel):
    email: EmailStr
    phone_number: str 

    _validate_phone_number = validator('phone_number', allow_reuse=True)(phone_number_validator)
    class Config:
        json_schema_extra = {
            'phone_number': {
                'regex': r'^\+?\d{1,4}[\s\d]{2,14}$'
            }
        }

class AddressFieldsMixin(BaseModel):
    residential_addr: str



#Centre
class CentreBase(BaseModel):
    location: str
    region: Optional[str]

class CentreCreate(CentreBase):
    pass

class CentreUpdate(CentreBase):
    pass

class CentreInDBBase(CentreBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Centre(CentreInDBBase):
    pass


#Directorate
class DirectorateBase(BaseModel):
    name: str
    centre_id: UUID

class DirectorateCreate(DirectorateBase):
    pass

class DirectorateUpdate(DirectorateBase):
    pass

class DirectorateInDBBase(DirectorateBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Directorate(DirectorateInDBBase):
    pass


#Grade
class GradeBase(BaseModel):
    name: str
    min_sal: float
    max_sal: float

class GradeCreate(GradeBase):
    pass

class GradeUpdate(GradeBase):
    pass

class GradeInDBBase(GradeBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Grade(GradeInDBBase):
    pass


#EmploymentType
class EmploymentTypeBase(BaseModel):
    name: str
    description: Optional[str]
    grade_id: UUID

class EmploymentTypeCreate(EmploymentTypeBase):
    pass

class EmploymentTypeUpdate(EmploymentTypeBase):
    pass

class EmploymentTypeInDBBase(EmploymentTypeBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class EmploymentType(EmploymentTypeInDBBase):
    pass


#StaffCategory
class StaffCategoryBase(BaseModel):
    category: str

class StaffCategoryCreate(StaffCategoryBase):
    pass

class StaffCategoryUpdate(StaffCategoryBase):
    pass

class StaffCategoryInDBBase(StaffCategoryBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class StaffCategory(StaffCategoryInDBBase):
    pass



#BioData
class BioDataBase(BaseModel):
    title: Title = Title.Other
    first_name: str
    other_names: Optional[str]
    surname: str
    previous_name: Optional[str]
    gender: Gender = Gender.Other
    date_of_birth: date
    nationality: str
    hometown: str
    religion: Optional[str]
    marital_status: MaritalStatus = MaritalStatus.Other
    residential_addr: str
    active_phone_number: str
    email: EmailStr
    ssnit_number: str
    ghana_card_number: str
    is_physically_challenged: bool
    disability: Optional[str]
    image_col: Optional[str] = None

class BioDataCreate(BioDataBase):
    pass

class BioDataUpdate(BioDataBase):
    pass

class BioDataInDBBase(BioDataBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class BioData(BioDataInDBBase):
    pass

#Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

#User
class UserBase(BaseModel):
    bio_row_id: UUID
    username: str
    email: Optional[EmailStr]
    hashed_password: str
    reset_pwd_token: Optional[str]
    is_active: bool = True
    role: str = "user"

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserInDBBase(UserBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass


#EmploymentDetail
class EmploymentDetailBase(BaseModel):
    bio_row_id: UUID
    date_of_first_appointment: date
    grade_on_first_appointment: Optional[str]
    grade_on_current_appointment_id: UUID
    directorate_id: UUID
    employee_number: str
    employment_type_id: UUID
    staff_category_id: UUID

class EmploymentDetailCreate(EmploymentDetailBase):
    pass

class EmploymentDetailUpdate(EmploymentDetailBase):
    pass

class EmploymentDetailInDBBase(EmploymentDetailBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class EmploymentDetail(EmploymentDetailInDBBase):
    pass



#BankDetail
class BankDetailBase(BaseModel):
    bio_row_id: UUID
    bank_name: str
    bank_branch: str
    account_number: str
    account_type: str
    account_status: Optional[str]

class BankDetailCreate(BankDetailBase):
    pass

class BankDetailUpdate(BankDetailBase):
    pass

class BankDetailInDBBase(BankDetailBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class BankDetail(BankDetailInDBBase):
    pass



#Academic
class AcademicBase(BaseModel):
    bio_row_id: UUID
    institution: str
    year: date
    programme: Optional[str]
    qualification: Optional[str]

class AcademicCreate(AcademicBase):
    pass

class AcademicUpdate(AcademicBase):
    pass

class AcademicInDBBase(AcademicBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Academic(AcademicInDBBase):
    pass


#Professional
class ProfessionalBase(BaseModel):
    bio_row_id: UUID
    year: date
    certification: str
    institution: str
    location: Optional[str]

class ProfessionalCreate(ProfessionalBase):
    pass

class ProfessionalUpdate(ProfessionalBase):
    pass

class ProfessionalInDBBase(ProfessionalBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Professional(ProfessionalInDBBase):
    pass


#Qualification
class QualificationBase(BaseModel):
    bio_row_id: UUID
    academic_qualification_id: UUID
    professional_qualification_id: UUID

class QualificationCreate(QualificationBase):
    pass

class QualificationUpdate(QualificationBase):
    pass

class QualificationInDBBase(QualificationBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Qualification(QualificationInDBBase):
    pass


#EmploymentHistory
class EmploymentHistoryBase(BaseModel):
    bio_row_id: UUID
    date_employed: date
    institution: str
    position: str
    end_date: Optional[date]

class EmploymentHistoryCreate(EmploymentHistoryBase):
    pass

class EmploymentHistoryUpdate(EmploymentHistoryBase):
    pass

class EmploymentHistoryInDBBase(EmploymentHistoryBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class EmploymentHistory(EmploymentHistoryInDBBase):
    pass



#FamilyInfo
class FamilyInfoBase(BaseModel):
    bio_row_id: UUID
    name_of_spouse: Optional[str]
    occupation: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    name_of_father_guardian: Optional[str]
    fathers_occupation: Optional[str]
    fathers_contact: Optional[str]
    fathers_address: Optional[str]
    name_of_mother_guardian: Optional[str]
    mothers_occupation: Optional[str]
    mothers_contact: Optional[str]
    mothers_address: Optional[str]
    children_name: Optional[str]
    children_dob: Optional[str]

class FamilyInfoCreate(FamilyInfoBase):
    pass

class FamilyInfoUpdate(FamilyInfoBase):
    pass

class FamilyInfoInDBBase(FamilyInfoBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class FamilyInfo(FamilyInfoInDBBase):
    pass



#EmergencyContact
class EmergencyContactBase(BaseModel):
    bio_row_id: UUID
    name: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    email: Optional[EmailStr]

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(EmergencyContactBase):
    pass

class EmergencyContactInDBBase(EmergencyContactBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class EmergencyContact(EmergencyContactInDBBase):
    pass



#NextOfKin
class NextOfKinBase(BaseModel):
    bio_row_id: UUID
    title: Title = Title.Other
    first_name: str
    other_name: Optional[str]
    surname: str
    gender: Gender = Gender.Other
    relation: str
    address: Optional[str]
    town: str
    region: str
    phone: str
    email: EmailStr

class NextOfKinCreate(NextOfKinBase):
    pass

class NextOfKinUpdate(NextOfKinBase):
    pass

class NextOfKinInDBBase(NextOfKinBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class NextOfKin(NextOfKinInDBBase):
    pass


#Declaration
class DeclarationBase(BaseModel):
    bio_row_id: UUID
    status: bool = False
    reps_signature: Optional[str] =None
    employees_signature: Optional[str] = None
    declaration_date: Optional[date] = None

class DeclarationCreate(DeclarationBase):
    pass

class DeclarationUpdate(DeclarationBase):
    pass

class DeclarationInDBBase(DeclarationBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Declaration(DeclarationInDBBase):
    pass


class TrademarkBase(BaseModel):
    name: str
    left_logo : Optional[str] = None
    right_logo: Optional[str] = None

class TrademarkCreate(TrademarkBase):
    pass

class TrademarkUpdate(TrademarkBase):
    pass

class TrademarkInDBBase(TrademarkBase, BaseSchema):
    pass

    class Config:
        orm_mode = True

class Trademark(TrademarkInDBBase):
    pass








