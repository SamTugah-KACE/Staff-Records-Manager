from models import *
from sqladmin import ModelView
from sqlalchemy import Column


# from fastapi_storages import FileSystemStorage
# from fastapi_storages.integrations.sqlalchemy import FileType


# storage = FileSystemStorage(path="uploads/db_files")

# List of all models
all_models = [
    Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, 
    BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User, Trademark
]
 
class Trademark(ModelView, model=Trademark):
    column_list = [Trademark.id, Trademark.name, Trademark.left_logo, Trademark.right_logo, Trademark.created_at]

class Center(ModelView, model=Centre):
    column_list = [Centre.id, Centre.location, Centre.region, Centre.created_at]

class Directorate(ModelView, model=Directorate):
    column_list = [Directorate.id, Directorate.location, Directorate.name, Directorate.created_at]

class Grade(ModelView, model=Grade):
    column_list = [Grade.id, Grade.name, Grade.min_sal, Grade.max_sal, Grade.created_at]

class EmploymentType(ModelView, model=EmploymentType):
    column_list = [EmploymentType.id, EmploymentType.name, EmploymentType.description, EmploymentType.grade_id, EmploymentType.created_at]

class StaffCategory(ModelView, model=StaffCategory):
    column_list = [StaffCategory.id, StaffCategory.category,  StaffCategory.created_at]


class Staff(ModelView, model=BioData):
    column_list = [BioData.id, BioData.title, BioData.first_name, BioData.surname, BioData.active_phone_number, BioData.email]

class EmploymentDetail(ModelView, model=EmploymentDetail):
    column_list = [EmploymentDetail.id, EmploymentDetail.date_of_first_appointment,  EmploymentDetail.grade_on_current_appointment_id, EmploymentDetail.directorate_id, EmploymentDetail.employment_type_id, EmploymentDetail.employee_number, EmploymentDetail.created_at]

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.bio_row_id, User.email, User.username, User.hashed_password, User.role]

class FamilyInfo(ModelView, model=FamilyInfo):
    column_list = [FamilyInfo.id, FamilyInfo.bio_row_id, FamilyInfo.name_of_spouse, FamilyInfo.occupation, FamilyInfo.created_at]

class EmergencyContact(ModelView, model=EmergencyContact):
    column_list = [EmergencyContact.id, EmergencyContact.bio_row_id, EmergencyContact.name,  EmergencyContact.phone_number, EmergencyContact.email, EmergencyContact.created_at]

class NextOfKin(ModelView, model=NextOfKin):
    column_list = [NextOfKin.id, NextOfKin.bio_row_id, NextOfKin.first_name, NextOfKin.surname, NextOfKin.phone, NextOfKin.created_at]

class BankDetail(ModelView, model=BankDetail):
    column_list = [BankDetail.id, BankDetail.bio_row_id, BankDetail.bank_name, BankDetail.bank_branch,  BankDetail.account_number, BankDetail.account_type, BankDetail.account_status, BankDetail.created_at]

class Academic(ModelView, model=Academic):
    column_list = [Academic.id, Academic.bio_row_id, Academic.programme, Academic.institution, Academic.year, Academic.created_at]

class Professional(ModelView, model=Professional):
    column_list = [Professional.id, Professional.bio_row_id, Professional.certification, Professional.institution, Professional.year, Professional.location, Professional.created_at]

class Qualification(ModelView, model=Qualification):
    column_list = [Qualification.id, Qualification.bio_row_id, Qualification.academic_qualification_id, Qualification.professional_qualification_id, Qualification.created_at]

class EmploymentHistory(ModelView, model=EmploymentHistory):
    column_list = [EmploymentHistory.id, EmploymentHistory.bio_row_id, EmploymentHistory.date_employed, EmploymentHistory.institution, EmploymentHistory.position, EmploymentHistory.end_date, EmploymentHistory.created_at]

class Declaration(ModelView, model=Declaration):
    column_list = [Declaration.id, Declaration.bio_row_id, Declaration.status, Declaration.employees_signature, Declaration.reps_signature, Declaration.declaration_date, Declaration.created_at]


# class DB(Base):
#     __tablename__ = "db_sql"

#     #id = Column(Integer, primary_key=True)    
#     file = Column(FileType(storage=storage))

# class DB(ModelView, model=DB):
#     column_list = [DB.file]

