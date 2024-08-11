from models import *
from sqladmin import Admin, ModelView
from .history.app.models_20240807120745 import EmploymentDetail



# List of all models
all_models = [
    Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, 
    BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]



class Center(ModelView, model=Centre):
    column_list = [Centre.id, Centre.location, Centre.region, Centre.created_at]

class Directorate(ModelView, model=Directorate):
    column_list = [Directorate.id, Directorate.centre_id, Directorate.name, Directorate.created_at]

class Grade(ModelView, model=Grade):
    column_list = [Grade.id, Grade.name, Grade.min_sal, Grade.max_sal, Grade.created_at]

class EmploymentType(ModelView, model=EmploymentType):
    column_list = [EmploymentType.id, EmploymentType.name, EmploymentType.grade_id, EmploymentType.description, EmploymentType.created_at]

class StaffCategory(ModelView, model=StaffCategory):
    column_list = [StaffCategory.id, StaffCategory.category,  StaffCategory.created_at]

class Staff(ModelView, model=BioData):
    column_list = [BioData.id, BioData.title, BioData.first_name, BioData.surname, BioData.active_phone_number, BioData.email]

class EmploymentDetail(ModelView, model=EmploymentDetail):
    column_list = [EmploymentDetail.id, EmploymentDetail.date_of_first_appointment,  EmploymentDetail.grade_on_current_appointment_id, EmploymentDetail.directorate_id, EmploymentDetail.employment_type_id, EmploymentDetail.employee_number, EmploymentDetail.created_at]

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.bio_row_id, User.email, User.username, User.hashed_password, User.role]

