from datetime import date
from fastapi import APIRouter, Depends, Form, HTTPException, Query, status, UploadFile, File, WebSocket, WebSocketDisconnect
from pydantic import EmailStr
import sqlalchemy
from sqlalchemy.orm import Session
from database.db_session import get_db
from auth import authenticate_user,create_access_token
from datetime import datetime, timedelta
from Config.config import settings
import schemas
from models import (BioData, EmploymentDetail, BankDetail, Academic, Professional, 
                        Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, 
                        NextOfKin, Declaration, StaffCategory, Centre, User, Directorate, Grade, EmploymentType, Trademark, UserRole)
from crud import (bio_data, declaration, 
                  user, trademark)

from typing import List, Optional, Type,  Union, Dict, Any
from fastapi.responses import FileResponse
import os
from crud import generate_pdf_for_bio_data
import crud
from _crud import (centre, employment_type, grade, directorate, staff_category, bank_detail, emergency_contact, employment_detail, employment_history, 
                  next_of_kin, family_info, academic, professional, qualification, role)

from auth import current_active_user, current_active_admin, current_active_admin_user
from uuid import UUID
import tempfile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request,Form
from passlib.context import CryptContext
from mail import *
from auth import get_password_hash

templates = Jinja2Templates(directory="templates")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)


# List of connected clients
clients: List[WebSocket] = []

# List of all models
all_models = [
    Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, 
    BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]


# Assuming you have a list of all models you want to include in the search
search_models = [Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, Declaration]


bio_data_related_models  = [
    EmploymentDetail, BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]


api_router = APIRouter()


@api_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("user-login.html", {"request": request})


@api_router.get("/search/", response_model=Dict[str, List[Dict[str, Any]]], tags=["Search Space"])
def search(search_string: str, db: Session = Depends(get_db), current_user: User = Depends(current_active_admin_user)):
    print("\ncurrent-user in search api: ", current_user)
    results = crud.search_all(db, search_string, search_models, current_user)
    return results

#Business Brand
@api_router.post("/logo/", response_model=schemas.Trademark, tags=["Business Brand - (HR Dashboard)"])
def create_business(
    *,
    db: Session = Depends(get_db),
    trade_in: schemas.TrademarkCreate = Depends(),
    left_logo: UploadFile = File(None),
    right_logo: UploadFile = File(None),
    
) -> Trademark:
    logo_obj = trademark.get_by_field(db, "name", trade_in.name)
    if logo_obj:
        raise HTTPException(status_code=400, detail="Business Info already exists")
    return trademark.create(db=db, obj_in=trade_in, file=left_logo, file2=right_logo)


@api_router.post("/console/logo/", response_model=schemas.Trademark, tags=["Business Brand - (HR Dashboard)"])
def create_business(
    *,
    db: Session = Depends(get_db),
    trade_in: schemas.TrademarkCreate = Depends(),
    left_logo: UploadFile = File(None),
    right_logo: UploadFile = File(None),
) -> Trademark:
    logo_obj = trademark.get_by_field(db, "name", trade_in.name)
    if logo_obj:
        raise HTTPException(status_code=400, detail="Business Info already exists")

    # Save the uploaded files if they exist
    left_logo_path = crud.save_and_resize_image(left_logo, f"{trade_in.name}_left.jpg") if left_logo else None
    right_logo_path = crud.save_and_resize_image(right_logo, f"{trade_in.name}_right.jpg") if right_logo else None

    # Set the file paths in the input schema
    trade_in.left_logo = left_logo_path
    trade_in.right_logo = right_logo_path

    return trademark.create(db=db, obj_in=trade_in)




@api_router.get("/logo/get/{id}", response_model=schemas.Trademark,  tags=["Business Brand - (HR Dashboard)"])
def read_business_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> Trademark:
    trademark_obj = trademark.get(db=db, id=id)
    if not trademark_obj:
        raise HTTPException(status_code=404, detail="Business Data not found")
    return trademark_obj

@api_router.get("/logos/", response_model=List[schemas.Trademark],  tags=["Business Brand - (HR Dashboard)"])
def read_businesses_info(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
    
) -> List[Trademark]:
    trademark_obj = trademark.get_multi(db=db, skip=skip, limit=limit)
    return trademark_obj


@api_router.put("/logo/update/{id}", response_model=schemas.Trademark,  tags=["Business Brand - (HR Dashboard)"])
def update_business_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    trademark_in: schemas.TrademarkUpdate= Depends(),
    left_logo: UploadFile = File(None),
    right_logo: UploadFile = File(None),
    
) -> Trademark:
    logo_obj = trademark.get(db=db, id=id)
    if not logo_obj:
        raise HTTPException(status_code=404, detail="Business Data not found")
    return trademark.update(db=db, db_obj=logo_obj, obj_in=trademark_in, file=left_logo, file2=right_logo)


@api_router.put("/console/logo/update/{id}", response_model=schemas.Trademark, tags=["Business Brand - (HR Dashboard)"])
def update_business_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    trademark_in: schemas.TrademarkUpdate = Depends(),
    left_logo: UploadFile = File(None),
    right_logo: UploadFile = File(None),
) -> Trademark:
    logo_obj = trademark.get(db=db, id=id)
    if not logo_obj:
        raise HTTPException(status_code=404, detail="Business Data not found")

    # Save the uploaded files if they exist
    if left_logo:
        left_logo_path = crud.save_and_resize_image(left_logo, f"{trademark_in.name}_left.jpg")
        trademark_in.left_logo = left_logo_path

    if right_logo:
        right_logo_path = crud.save_and_resize_image(right_logo, f"{trademark_in.name}_right.jpg")
        trademark_in.right_logo = right_logo_path

    return trademark.update(db=db, db_obj=logo_obj, obj_in=trademark_in)


@api_router.delete("/logo/{id}",   tags=["Business Brand - (HR Dashboard)"])
def delete_business_data(
    *,
    db: Session = Depends(get_db),
    id: str,
    
):
    logo_obj = trademark.get(db=db, id=id)
    if not logo_obj:
        raise HTTPException(status_code=404, detail="Business Data not found")
    return trademark.delete_trademark(db, id)




#Centre
@api_router.post("/centre/", response_model=schemas.Centre, tags=["Centre"])
def create_centre(
    *,
    db: Session = Depends(get_db),
    request: Request,
    location: Optional[str] = Form(None),
    region: Optional[str] = Form(None)
    #centre_in: schemas.CentreCreate,
    
) -> Centre:
    centre_obj = centre.get_by_field(db, "location", location)
    if centre_obj:
        raise HTTPException(status_code=400, detail="Centre already exists")
    
    centre_in = Centre()
    centre_in.location=location
    centre_in.region=region
    db.add(centre_in)
    db.commit()
    db.refresh(centre_in)
    return templates.TemplateResponse("admin-dashboard.html", {"request": request})

@api_router.get("/centre/{id}", response_model=schemas.Centre,  tags=["Centre"])
def read_centre(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> Centre:
    centre_obj = centre.get(db=db, id=id)
    if not centre_obj:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre_obj

@api_router.get("/centres/", response_model=List[schemas.Centre],  tags=["Centre"])
def read_centres(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
    
) -> List[Centre]:
    centre_obj = centre.get_multi(db, skip, limit)
    
    return centre_obj


@api_router.put("/centre/{id}", response_model=schemas.Centre,  tags=["Centre"])
def update_centre(
    *,
    db: Session = Depends(get_db),
    id: str,
    centre_in: schemas.CentreUpdate,
    
) -> Centre:
    centre_obj = centre.get(db=db, id=id)
    if not centre_obj:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre.update(db=db, db_obj=centre_obj, obj_in=centre_in)

@api_router.delete("/centre/rm/{id}", response_model=schemas.Centre,  tags=["Centre"])
def delete_centre(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> Centre:
    centre_obj = centre.get(db=db, id=id)
    if not centre_obj:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre.remove(db=db, id=id, force_delete=force_delete)







#Directorate
@api_router.post("/directorate/", response_model=schemas.Directorate, tags=["Directorate"])
def create_directorate(
    *,
    request: Request,
    db: Session = Depends(get_db),
    name: Optional[str] = Form(None),
    centre_id: Optional[str] = Form(None),
    #directorate_in: schemas.DirectorateCreate,
    
) -> Directorate:
    directorate_obj = directorate.get_by_field(db, "name", name)
    if directorate_obj:
        raise HTTPException(status_code=400, detail="directorate already exists")
    
    directorate_in = Directorate()
    directorate_in.name=name
    directorate_in.centre_id=centre_id
    db.add(directorate_in)
    db.commit()
    db.refresh(directorate_in)

    return templates.TemplateResponse("admin-dashboard.html", {"request": request})
    #return directorate.create(db=db, obj_in=directorate_in)






@api_router.get("/directorates/", response_model=List[schemas.DirectorateResponse],  tags=["Directorate"])
def read_directorates(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.DirectorateResponse]:
    directorate_obj = directorate.get_multi_with_model(db, model=Directorate, skip=skip, limit=limit)
    return directorate_obj

@api_router.get("/directorate/{id}", response_model=schemas.DirectorateResponse,  tags=["Directorate"])
def read_directorate(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.DirectorateResponse:
    directorate_obj = directorate.get_detailed(db=db, model=Directorate, id=id)
    if not directorate_obj:
        raise HTTPException(status_code=404, detail="directorate not found")
    return directorate_obj

@api_router.put("/directorate/{id}", response_model=schemas.Directorate,  tags=["Directorate"])
def update_directorate(
    *,
    db: Session = Depends(get_db),
    id: str,
    directorate_in: schemas.DirectorateUpdate,
    
) -> Directorate:
    directorate_obj = directorate.get(db=db, id=id)
    if not directorate_obj:
        raise HTTPException(status_code=404, detail="directorate not found")
    return directorate.update(db=db, db_obj=directorate_obj, obj_in=directorate_in)

@api_router.delete("/directorate/rm/{id}", response_model=schemas.Directorate,  tags=["Directorate"])
def delete_directorate(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> Directorate:
    directorate_obj = directorate.get(db=db, id=id)
    if not directorate_obj:
        raise HTTPException(status_code=404, detail="directorate not found")
    return directorate.remove(db=db, id=id, force_delete=force_delete)


#Grade
@api_router.post("/grade/", response_model=schemas.Grade, tags=["Grade"])
def create_grade(
    *,
    db: Session = Depends(get_db),
    request: Request,
    name: Optional[str] = Form(None),
    min_sal: Optional[str] = Form(None),
    max_sal: Optional[str] = Form(None)
    #grade_in: schemas.GradeCreate,
    
) -> Grade:
    grade_obj = grade.get_by_field(db, "name", name)
    if grade_obj:
        raise HTTPException(status_code=400, detail="grade already exists")
    
    grade_in = Grade()
    grade_in.name=name
    grade_in.min_sal=min_sal
    grade_in.max_sal=max_sal
    db.add(grade_in)
    db.commit()
    db.refresh(grade_in)

    return templates.TemplateResponse("admin-dashboard.html", {"request": request})
    #return grade.create(db=db, obj_in=grade_in)

@api_router.get("/grades/", response_model=List[schemas.Grade],  tags=["Grade"])
def read_grades(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[Grade]:
    grade_obj = grade.get_multi(db, skip=skip, limit=limit)
    return grade_obj

@api_router.get("/grade/{id}", response_model=schemas.Grade,  tags=["Grade"])
def read_grade(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> Grade:
    grade_obj = grade.get(db=db, id=id)
    if not grade_obj:
        raise HTTPException(status_code=404, detail="grade not found")
    return grade_obj

@api_router.put("/grade/{id}", response_model=schemas.Grade,  tags=["Grade"])
def update_grade(
    *,
    db: Session = Depends(get_db),
    id: str,
    grade_in: schemas.GradeUpdate,
    
) -> Grade:
    grade_obj = grade.get(db=db, id=id)
    if not grade_obj:
        raise HTTPException(status_code=404, detail="grade not found")
    return grade.update(db=db, db_obj=grade_obj, obj_in=grade_in)

@api_router.delete("/grade/rm/{id}", response_model=schemas.Grade,  tags=["Grade"])
def delete_grade(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> Grade:
    grade_obj = grade.get(db=db, id=id)
    if not grade_obj:
        raise HTTPException(status_code=404, detail="grade not found")
    return grade.remove(db=db, id=id, force_delete=force_delete)


#Employment Type
@api_router.post("/employment_type/", response_model=schemas.EmploymentType, tags=["Employment Type"])
def create_employment_type(
    *,
    db: Session = Depends(get_db),
    request: Request,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    grade_id: Optional[str] = Form(None),
    #employment_type_in: schemas.EmploymentTypeCreate,
    
) -> EmploymentType:
    employment_type_obj = employment_type.get_by_field(db, "name", name)
    if employment_type_obj:
        raise HTTPException(status_code=400, detail="employment_type already exists")
    
    employment_type_in = EmploymentType()
    employment_type_in.name=name
    employment_type_in.description=description
    employment_type_in.grade_id=grade_id
    db.add(employment_type_in)
    db.commit()
    db.refresh(employment_type_in)
    return templates.TemplateResponse("admin-dashboard.html", {"request": request})
    # return employment_type.create(db=db, obj_in=employment_type_in)

@api_router.get("/employment_types/", response_model=List[schemas.EmploymentTypeResponse],  tags=["Employment Type"])
def read_employment_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.EmploymentTypeResponse]:
    employment_type_obj = employment_type.get_multi_with_model(db, model=EmploymentType, skip=skip, limit=limit)
    return employment_type_obj

@api_router.get("/employment_type/{id}", response_model=schemas.EmploymentTypeResponse,  tags=["Employment Type"])
def read_employment_type(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.EmploymentTypeResponse:
    employment_type_obj = employment_type.get_detailed(db=db, model=EmploymentType, id=id)
    if not employment_type_obj:
        raise HTTPException(status_code=404, detail="employment_type not found")
    return employment_type_obj

@api_router.put("/employment_type/{id}", response_model=schemas.EmploymentType,  tags=["Employment Type"])
def update_employment_type(
    *,
    db: Session = Depends(get_db),
    id: str,
    employment_type_in: schemas.EmploymentTypeUpdate,
    
) -> EmploymentType:
    employment_type_obj = employment_type.get(db=db, id=id)
    if not employment_type_obj:
        raise HTTPException(status_code=404, detail="employment_type not found")
    return employment_type.update(db=db, db_obj=employment_type_obj, obj_in=employment_type_in)

@api_router.delete("/employment_type/rm/{id}", response_model=schemas.EmploymentType,  tags=["Employment Type"])
def delete_employment_type(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> EmploymentType:
    employment_type_obj = employment_type.get(db=db, id=id)
    if not employment_type_obj:
        raise HTTPException(status_code=404, detail="employment_type not found")
    return employment_type.remove(db=db, id=id, force_delete=force_delete)


#Staff Category
@api_router.post("/staff_category/", response_model=schemas.StaffCategory, tags=["Staff Category"])
def create_staff_category(
    *,
    db: Session = Depends(get_db),
    request: Request,
    category: Optional[str] = Form(None),
    #staff_category_in: schemas.StaffCategoryCreate,
    
) -> StaffCategory:
    staff_category_obj = staff_category.get_by_field(db, "category", category)
    if staff_category_obj:
        raise HTTPException(status_code=400, detail="staff_category already exists")
    
    staff_category_in = StaffCategory()
    staff_category_in.category=category
    db.add(staff_category_in)
    db.commit()
    db.refresh(staff_category_in)
    return templates.TemplateResponse("admin-dashboard.html", {"request": request})
    #return staff_category.create(db=db, obj_in=staff_category_in)

@api_router.get("/staff_categories/", response_model=List[schemas.StaffCategory],  tags=["Staff Category"])
def read_staff_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[StaffCategory]:
    staff_category_obj = staff_category.get_multi(db, skip=skip, limit=limit)
    return staff_category_obj

@api_router.get("/staff_category/{id}", response_model=schemas.StaffCategory,  tags=["Staff Category"])
def read_staff_category(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> StaffCategory:
    staff_category_obj = staff_category.get(db=db, id=id)
    if not staff_category_obj:
        raise HTTPException(status_code=404, detail="staff_category not found")
    return staff_category_obj

@api_router.put("/staff_category/{id}", response_model=schemas.StaffCategory,  tags=["Staff Category"])
def update_staff_category(
    *,
    db: Session = Depends(get_db),
    id: str,
    staff_category_in: schemas.StaffCategoryUpdate,
    
) -> StaffCategory:
    staff_category_obj = staff_category.get(db=db, id=id)
    if not staff_category_obj:
        raise HTTPException(status_code=404, detail="staff_category not found")
    return staff_category.update(db=db, db_obj=staff_category_obj, obj_in=staff_category_in)

@api_router.delete("/staff_category/rm/{id}", response_model=schemas.StaffCategory,  tags=["Staff Category"])
def delete_staff_category(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> StaffCategory:
    staff_category_obj = staff_category.get(db=db, id=id)
    if not staff_category_obj:
        raise HTTPException(status_code=404, detail="staff_category not found")
    return staff_category.remove(db=db, id=id, force_delete=force_delete)








@api_router.get("/bio_data/create", response_class=HTMLResponse)
def user_biodata_registration(request: Request):

    return templates.TemplateResponse("create-biodata.html", {"request": request})



#BioData
@api_router.post("/bio_data_/", response_model=schemas.BioData, tags=["BioData"])
async def create_bio_data_(
    *,
    request: Request,
    db: Session = Depends(get_db),
    #bio_data_in: schemas.BioDataCreate,
    title: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    other_names: Optional[str] = Form(None),
    surname: Optional[str] = Form(None),
    previous_name: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    nationality: Optional[str] = Form(None),
    hometown: Optional[str] = Form(None),
    religion: Optional[str] = Form(None),
    marital_status: Optional[str] = Form(None),
    residential_addr: Optional[str] = Form(None),
    active_phone_number: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    ssnit_number: Optional[str] = Form(None),
    ghana_card_number: Optional[str] = Form(None),
    is_physically_challenged: Optional[bool] = Form(None),
    disability: Optional[str] = Form(None),
    file: UploadFile = File(None),
    system_role: str = Form(None),
    current_user: User = Depends(current_active_admin_user),
) -> BioData:
    bio_data_obj = bio_data.get_by_field(db, "active_phone_number", active_phone_number)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="Phone Number Already Exists")
    bio_data_obj = bio_data.get_by_field(db, "email", email)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="Email Address Already Exists")
    bio_data_obj = bio_data.get_by_field(db, "ssnit_number", ssnit_number)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="Social Security Number Already Exists")
    bio_data_obj = bio_data.get_by_field(db, "ghana_card_number", ghana_card_number)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="National ID Number Already Exists")
    
    # if bio_data_obj:
    #      return templates.TemplateResponse("biodata-exist-error.html", {"request": request})
    # Retrieve user role from the UserRole table
    #user_role = db.query(UserRole).filter(UserRole.roles == current_user.role).first()
    print("user_role: ", current_user)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User role '{current_user}' is not authorized for this task.")

    # Generate username and password
    username = generate_username(first_name, surname)
    password = generate_password()


    bio_data_in = BioData()
    bio_data_in.title=title
    bio_data_in.first_name=first_name
    bio_data_in.other_names=other_names
    bio_data_in.surname=surname
    bio_data_in.previous_name=previous_name
    bio_data_in.gender=gender
    bio_data_in.date_of_birth=date_of_birth
    bio_data_in.nationality=nationality
    bio_data_in.hometown=hometown
    bio_data_in.religion=religion
    bio_data_in.marital_status=marital_status
    bio_data_in.residential_addr=residential_addr
    bio_data_in.active_phone_number=active_phone_number
    bio_data_in.email=email
    bio_data_in.ssnit_number=ssnit_number
    bio_data_in.ghana_card_number=ghana_card_number
    bio_data_in.is_physically_challenged=is_physically_challenged
    bio_data_in.disability=disability
    bio_data_in.registered_by = current_user.role
    
    files = {"image_col": file}
    new_biodata = bio_data.create(db=db, obj_in=bio_data_in, files=files)

     # Hash the password
    #hashed_password = get_password_hash(password)
    hashed_password = password

    # Prepare the user data
    user_data = {
        "bio_row_id": new_biodata.id,  # Using the generated bio-data ID
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role": system_role,  # Set role as 'user'
        "is_active": True
    }

    # Create the user in the User table
    new_user = create_user_(
        request=request,
        bio_row_id=user_data['bio_row_id'],
        username=user_data['username'],
        email=user_data['email'],
        hashed_password=user_data['hashed_password'],
        role=user_data['role'],
        db=db
    )

    # Send email with credentials
    email_body = get_email_template(username, password, 'localhost:8000')
    await send_email(email=email, subject="Account Credentials", body=email_body)
    
    print("\n\n=======user registration status: ", new_user)
    return new_biodata

    #return templates.TemplateResponse("biodata-registration-success.html", {"request": request, "title": title, "first_name": first_name,"surname": surname,"email": email, "bio_row_id": new_biodata.id,})
    #return bio_data.create(db=db, obj_in=bio_data_in, files=files)




#BioData
@api_router.post("/bio_data/", response_model=schemas.BioData, tags=["BioData"])
def create_bio_data(
    *,
    request: Request,
    db: Session = Depends(get_db),
    #bio_data_in: schemas.BioDataCreate,
    title: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    other_names: Optional[str] = Form(None),
    surname: Optional[str] = Form(None),
    previous_name: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    nationality: Optional[str] = Form(None),
    hometown: Optional[str] = Form(None),
    religion: Optional[str] = Form(None),
    marital_status: Optional[str] = Form(None),
    residential_addr: Optional[str] = Form(None),
    active_phone_number: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    ssnit_number: Optional[str] = Form(None),
    ghana_card_number: Optional[str] = Form(None),
    is_physically_challenged: Optional[bool] = Form(None),
    disability: Optional[str] = Form(None),
    file: UploadFile = File(None),
    
) -> BioData:
    bio_data_obj = bio_data.get_by_field(db, "active_phone_number", active_phone_number)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="Phone Number Already Exists")
    bio_data_obj = bio_data.get_by_field(db, "email", email)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="Email Address Already Exists")
    bio_data_obj = bio_data.get_by_field(db, "ssnit_number", ssnit_number)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="Social Security Number Already Exists")
    bio_data_obj = bio_data.get_by_field(db, "ghana_card_number", ghana_card_number)
    if bio_data_obj:
        raise HTTPException(status_code=400, detail="National ID Number Already Exists")
    
    if bio_data_obj:
         return templates.TemplateResponse("biodata-exist-error.html", {"request": request})
    


    bio_data_in = BioData()
    bio_data_in.title=title
    bio_data_in.first_name=first_name
    bio_data_in.other_names=other_names
    bio_data_in.surname=surname
    bio_data_in.previous_name=previous_name
    bio_data_in.gender=gender
    bio_data_in.date_of_birth=date_of_birth
    bio_data_in.nationality=nationality
    bio_data_in.hometown=hometown
    bio_data_in.religion=religion
    bio_data_in.marital_status=marital_status
    bio_data_in.residential_addr=residential_addr
    bio_data_in.active_phone_number=active_phone_number
    bio_data_in.email=email
    bio_data_in.ssnit_number=ssnit_number
    bio_data_in.ghana_card_number=ghana_card_number
    bio_data_in.is_physically_challenged=is_physically_challenged
    bio_data_in.disability=disability
    
    files = {"image_col": file}
    new_biodata = bio_data.create(db=db, obj_in=bio_data_in, files=files)

    
    
    return new_biodata

    #return templates.TemplateResponse("biodata-registration-success.html", {"request": request, "title": title, "first_name": first_name,"surname": surname,"email": email, "bio_row_id": new_biodata.id,})
    #return bio_data.create(db=db, obj_in=bio_data_in, files=files)

@api_router.get("/staff_bio_data/", response_model=List[schemas.BioData], tags=["BioData"])
def read__staff_bio_data(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[BioData]:
    bio_data_list = bio_data.get_multi(db, skip=skip, limit=limit)
    return bio_data_list

@api_router.get("/bio_data/{id}", response_model=schemas.BioData, tags=["BioData"])
def read_bio_data(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> BioData:
    bio_data_obj = bio_data.get(db=db, id=id)
    if not bio_data_obj:
        raise HTTPException(status_code=404, detail="bio_data not found")
    return bio_data_obj

@api_router.put("/bio_data/{id}", response_model=schemas.BioData,  tags=["BioData"])
def update_bio_data(
    *,
    db: Session = Depends(get_db),
    id: str,
    title: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    other_names: Optional[str] = Form(None),
    surname: Optional[str] = Form(None),
    previous_name: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    nationality: Optional[str] = Form(None),
    hometown: Optional[str] = Form(None),
    religion: Optional[str] = Form(None),
    marital_status: Optional[str] = Form(None),
    residential_addr: Optional[str] = Form(None),
    active_phone_number: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    ssnit_number: Optional[str] = Form(None),
    ghana_card_number: Optional[str] = Form(None),
    is_physically_challenged: Optional[bool] = Form(None),
    disability: Optional[str] = Form(None),
    file: UploadFile = File(None),
    
) -> BioData:
    bio_data_obj = bio_data.get(db=db, id=id)
    print("bio_data_obj: ", bio_data_obj)
    if not bio_data_obj:
        raise HTTPException(status_code=404, detail="bio_data not found")
    
    bio_data_in = schemas.BioDataUpdate(
        title=title,
        first_name=first_name,
        other_names=other_names,
        surname=surname,
        previous_name=previous_name,
        gender=gender,
        date_of_birth=date_of_birth,
        nationality=nationality,
        hometown=hometown,
        religion=religion,
        marital_status=marital_status,
        residential_addr=residential_addr,
        active_phone_number=active_phone_number,
        email=email,
        ssnit_number=ssnit_number,
        ghana_card_number=ghana_card_number,
        is_physically_challenged=is_physically_challenged,
        disability=disability
    )
    files = {"image_col": file}
    return bio_data.update(db=db, db_obj=bio_data_obj, obj_in=bio_data_in, files=files)




@api_router.put("/bio_data/update_image/", response_model=schemas.BioData, tags=["BioData"])
def update_image(
    identifier: Union[str, UUID],
    image_file: UploadFile = File(...),
    identifier_field: str = 'id',
    db: Session = Depends(get_db)
):
    """
    Update only the image_col of a BioData record.
    - `identifier`: The UUID or unique field value to identify the record.
    - `identifier_field`: The field name used for identifying the record. Defaults to 'id'.
    - `image_file`: The new image file to be uploaded.
    """
    obj = crud.update_image_col(db, identifier, image_file, identifier_field)
    return obj



@api_router.delete("/bio_data/rm/{id}", response_model=schemas.BioData, tags=["BioData"])
def delete_bio_data(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False, description="Force delete the bio_data without confirmation")
) -> BioData:
    bio_data_obj = bio_data.get(db=db, id=id)
    if not bio_data_obj:
        raise HTTPException(status_code=404, detail="bio_data not found")

    return bio_data.remove(db=db, id=id, force_delete=force_delete)













@api_router.get("/user/login-form", response_class=HTMLResponse)
def user_login(request: Request):

    return templates.TemplateResponse("user-login.html", {"request": request})





@api_router.post("/user/auth-login", response_class=HTMLResponse)
def user_auth(request: Request, username:str = Form(...), hash_password:str = Form(...), db: Session = Depends(get_db)):

    user = authenticate_user(db=db, username=username, password=hash_password)
    if not user:
        return templates.TemplateResponse("login-error.html", {"request": request})
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    grades = db.query(Grade).all()
    directorates = db.query(Directorate).all()
    employment_types = db.query(EmploymentType).all()
    staff_categories = db.query(StaffCategory).all()
    centres = db.query(Centre).all()
    biodatas = db.query(BioData).all()

    if user.role == "admin":
        return templates.TemplateResponse("admin-dashboard.html", {"request": request, "grades": grades,"centres": centres, "biodatas": biodatas})
    else:
        return templates.TemplateResponse("user-dashboard.html", {"request": request, "bio_row_id": user.bio_row_id,
                                                                   "grades": grades,"directorates": directorates,"employment_types": employment_types,"staff_categories": staff_categories})




@api_router.get("/user/create", response_class=HTMLResponse)
def user_registration(request: Request, bio_row_id: str, db: Session = Depends(get_db)):

    email = db.query(BioData).filter(BioData.id == bio_row_id).first()

    return templates.TemplateResponse("user-create.html", {"request": request, "bio_row_id": bio_row_id, "email": email.email})




#users
# @api_router.post("/user", response_model=schemas.User,  tags=["Users"], status_code=status.HTTP_201_CREATED)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), ):
#     return crud.create_user(db=db, user=user)

@api_router.post("/user_",  tags=["Users"], status_code=status.HTTP_201_CREATED)
def create_user_(
    request: Request,
    bio_row_id: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    hashed_password: Optional[str] = Form(...),
    role: Optional[str] = Form(None),
    db: Session = Depends(get_db) 
    ):

    # Create user with hashed password
    #hash_password = get_password_hash(hashed_password)
    db_user = User()
    db_user.bio_row_id=bio_row_id
    db_user.username=username
    db_user.email = email
    db_user.hashed_password=hashed_password
    db_user.role=role,
    db_user.is_active=True
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)

    new_user = crud.create_user(db=db, user=db_user)
    return templates.TemplateResponse("user-registration-success.html", {"request": request, "username": new_user.username})


@api_router.post("/user",  tags=["Users"], status_code=status.HTTP_201_CREATED)
def create_user(
    request: Request,
    bio_row_id: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    hashed_password: Optional[str] = Form(...),
    role: Optional[str] = Form(None),
    db: Session = Depends(get_db) 
    ):

    # Create user with hashed password
    hash_password = get_password_hash(hashed_password)
    db_user = User()
    db_user.bio_row_id=bio_row_id
    db_user.username=username
    db_user.email = email
    db_user.hashed_password=hashed_password
    db_user.role=role,
    db_user.is_active=True
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)

    new_user = crud.create_user(db=db, user=db_user)
    return templates.TemplateResponse("user-registration-success.html", {"request": request, "username": new_user.username})




@api_router.get("/user/get/{user_id}", response_model=schemas.UserResponse, tags=["Users"])
def read_user(user_id: UUID, db: Session = Depends(get_db), ):
    db_user = crud.get_detailed_crud(db, model=User, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@api_router.get("/users", tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), ) -> List[schemas.UserResponse]:
    #users = crud.get_users(db, skip=skip, limit=limit)
    users = crud.get_multi_users_with_model(db, model=User, skip=skip, limit=limit)
    return users

@api_router.put("/user/update/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: UUID, user_update: schemas.UserUpdate, db: Session = Depends(get_db), ):
    return crud.update_user(db=db, user_id=user_id, user_update=user_update)


@api_router.put("/user/account/{email}",  tags=["Users"])
def update_user_account(email: str, status: bool, db: Session = Depends(get_db), ):
    return crud.activate_deactivate_account(db, email, status)


@api_router.delete("/users/rm/{user_id}", tags=["Users"])
def delete_user(user_id: UUID, db: Session = Depends(get_db), ):
    db_user = user.remove(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return "Data deleted successfully"




@api_router.websocket("/ws/staff")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Listen for data from client
            # Here you can process the data
    except WebSocketDisconnect:
        clients.remove(websocket)
    
# Function to broadcast updates to all clients
async def broadcast_update(message: str):
    for client in clients:
        await client.send_text(message)



#UserRole
@api_router.post("/role/", response_model=schemas.Role, tags=["Role"])
def create_Role(
    *,
    db: Session = Depends(get_db),
    request: Request,
    roles: Optional[str] = Form(None),
    dashboard: Optional[str] = Form(None)
    #Role_in: schemas.RoleCreate,
    
) -> UserRole:
    User_obj = role.get_by_field(db, "roles", roles)
    if User_obj:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    Role_in = UserRole()
    Role_in.roles=roles
    Role_in.dashboard=dashboard
    db.add(Role_in)
    db.commit()
    db.refresh(Role_in)
    return Role_in
    # return templates.TemplateResponse("admin-dashboard.html", {"request": request})

@api_router.get("/Role/{id}", response_model=schemas.Role,  tags=["Role"])
def read_Role(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> UserRole:
    Role_obj = role.get(db=db, id=id)
    if not Role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    return Role_obj



@api_router.get("/roles/",   tags=["Role"])
def read_Roles(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
    
) -> List[UserRole]:
    Role_obj = role.get_multi_field(db, skip, limit)
    
    return Role_obj


@api_router.get("/Roles/", response_model=List[schemas.Role],  tags=["Role"])
def read_Roles(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
    
) -> List[UserRole]:
    Role_obj = role.get_multi(db, skip, limit)
    
    return Role_obj


@api_router.put("/Role/{id}", response_model=schemas.Role,  tags=["Role"])
def update_Role(
    *,
    db: Session = Depends(get_db),
    id: str,
    Role_in: schemas.RoleUpdate,
    
) -> UserRole:
    Role_obj = role.get(db=db, id=id)
    if not Role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    return role.update(db=db, db_obj=Role_obj, obj_in=Role_in)

@api_router.delete("/Role/rm/{id}", response_model=schemas.Role,  tags=["Role"])
def delete_Role(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> UserRole:
    Role_obj = role.get(db=db, id=id)
    if not Role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    return role.remove(db=db, id=id, force_delete=force_delete)












@api_router.post("/declaration/", response_model=schemas.Declaration, tags=["Declaration"])
def create_declaration(
    *,
    request: Request,
    db: Session = Depends(get_db),
    #declaration_in: schemas.DeclarationCreate,
    bio_row_id: Optional[str] = Form(None),
    #status: Optional[bool] = Form(None),
    declaration_date: Optional[date] = Form(None),
    reps_signature: UploadFile = File(None),
    employees_signature: UploadFile = File(None)
) -> Any:
    

    declaration_in = schemas.DeclarationCreate(
        bio_row_id = bio_row_id,
        status=True,
        declaration_date=declaration_date
    )

    files = {
        'reps_signature': reps_signature.file.read() if reps_signature else None,
        'employees_signature': employees_signature.file.read() if employees_signature else None
    }

    declaration = crud.declaration.create(db=db, obj_in=declaration_in, files=files)
    return templates.TemplateResponse("user-dashboard.html", {"request": request, "bio_row_id": bio_row_id})


@api_router.get("/declarations", response_model=List[schemas.Declaration],  tags=["Declaration"])
def read_declarations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), ) -> List[Declaration]:
    decs = crud.declaration.get_multi_declarations(db, skip=skip, limit=limit)
    return decs


@api_router.get("/declaration/{id}", response_model=schemas.DeclarationResponse, tags=["Declaration"])
def read_declaration(declaration_id: UUID, db: Session = Depends(get_db), ):
    db_declaration = crud.get_detailed_crud(db, model=Declaration, id=declaration_id)
    if db_declaration is None:
        raise HTTPException(status_code=404, detail="Declaration not found")
    return db_declaration


@api_router.put("/update_declaration/{id}", response_model=schemas.Declaration, tags=["Declaration"])
def update_declaration(
    *,
    db: Session = Depends(get_db),
    id: UUID,
    bio_row_id: Optional[str] = Form(None),
    status: Optional[bool] = Form(None),
    reps_signature: UploadFile = File(None),
    employees_signature: UploadFile = File(None),
    declaration_date: Optional[date] = Form(None),
    
) -> Declaration:
    declarat = crud.declaration.get_declaration(db=db, id=id)
    if not declarat:
        raise HTTPException(status_code=404, detail="Declaration not found")

    # files = {
    #     'reps_signature': reps_signature.file.read() if reps_signature else None,
    #     'employees_signature': employees_signature.file.read() if employees_signature else None
    # }

    files = {
        'reps_signature': reps_signature if reps_signature else None,
        'employees_signature': employees_signature if employees_signature else None
    }

    declaration_in = schemas.DeclarationUpdate(
        bio_row_id=bio_row_id,
        status=status,
        declaration_date=declaration_date
    )

    declaratio = crud.declaration.update(db=db, db_obj=declarat, obj_in=declaration_in, files=files)

    return declaratio

@api_router.delete("/declaration/rm/{id}", response_model=schemas.Declaration, tags=["Declaration"])
def delete_declaration(
    *,
    db: Session = Depends(get_db),
    id: UUID,
    force_delete: bool = Query(False, description="Force delete related data"),
    
) -> Any:
    if not force_delete:
        # Simulate user prompt by requiring an additional confirmation parameter
        raise HTTPException(status_code=400, detail="Are you sure you want to delete all related data? This action is irreversible. Set force_delete=True to confirm.")
    
    declaration = crud.declaration.remove(db=db, id=id, force_delete=force_delete)
    return declaration





@api_router.post("/employment_detail/", response_model=schemas.EmploymentDetail, tags=["Employment Detail"])
def create_employment_detail(
    *,
    request: Request,
    db: Session = Depends(get_db),
    bio_row_id: Optional[str] = Form(None),
    date_of_first_appointment: Optional[date] = Form(None),
    grade_on_first_appointment: Optional[str] = Form(None),
    grade_on_current_appointment_id: Optional[str] = Form(None),
    directorate_id: Optional[str] = Form(None),
    employee_number: Optional[str] = Form(None),
    employment_type_id: Optional[str] = Form(None),
    staff_category_id: Optional[str] = Form(None),
    #employment_detail_in: schemas.EmploymentDetailCreate,
    
) -> EmploymentDetail:
    employment_detail_obj = employment_detail.get_by_field(db, "bio_row_id", bio_row_id)
    if employment_detail_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    employment_detail_obj = employment_detail.get_by_field(db, "employee_number", employee_number)
    if employment_detail_obj:
        raise HTTPException(status_code=400, detail="Employee Number already exists")
    
    if employment_detail_obj:
         return templates.TemplateResponse("biodata-exist-error.html", {"request": request})
    
    employment_detail_in = EmploymentDetail()
    employment_detail_in.bio_row_id=bio_row_id
    employment_detail_in.date_of_first_appointment=date_of_first_appointment
    employment_detail_in.grade_on_first_appointment=grade_on_first_appointment
    employment_detail_in.grade_on_current_appointment_id=grade_on_current_appointment_id
    employment_detail_in.directorate_id=directorate_id
    employment_detail_in.employee_number=employee_number
    employment_detail_in.employment_type_id=employment_type_id
    employment_detail_in.staff_category_id=staff_category_id
    db.add(employment_detail_in)
    db.commit()
    db.refresh(employment_detail_in)

    #employment_detail.create(db=db, obj_in=employment_detail_in)
    return templates.TemplateResponse("user-dashboard.html", {"request": request, "bio_row_id": bio_row_id})









@api_router.get("/staff_employment_detail/", response_model=List[schemas.EmploymentDetailResponse],  tags=["Employment Detail"])
def read_all_staff_employment_detail(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.EmploymentDetailResponse]:
    employment_detail_obj = employment_detail.get_multi_with_model(db, model=EmploymentDetail, skip=skip, limit=limit)
    return employment_detail_obj

@api_router.get("/employment_detail/{id}", response_model=schemas.EmploymentDetailResponse,  tags=["Employment Detail"])
def read_employment_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.EmploymentDetailResponse:
    employment_detail_obj = employment_detail.get_detailed(db=db, model=EmploymentDetail, id=id)
    if not employment_detail_obj:
        raise HTTPException(status_code=404, detail="employment_detail not found")
    return employment_detail_obj

@api_router.put("/employment_detail/{id}", response_model=schemas.EmploymentDetail,  tags=["Employment Detail"])
def update_employment_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    employment_detail_in: schemas.EmploymentDetailUpdate,
    
) -> EmploymentDetail:
    employment_detail_obj = employment_detail.get(db=db, id=id)
    if not employment_detail_obj:
        raise HTTPException(status_code=404, detail="employment_detail not found")
    return employment_detail.update(db=db, db_obj=employment_detail_obj, obj_in=employment_detail_in)

@api_router.delete("/employment_detail/rm/{id}", response_model=schemas.EmploymentDetail,  tags=["Employment Detail"])
def delete_employment_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> EmploymentDetail:
    employment_detail_obj = employment_detail.get(db=db, id=id)
    if not employment_detail_obj:
        raise HTTPException(status_code=404, detail="employment_detail not found")
    return employment_detail.remove(db=db, id=id, force_delete=force_delete)


















#BankDetail
@api_router.post("/bank_detail/", response_model=schemas.BankDetail, tags=["Bank Detail"])
def create_bank_detail(
    *,
    db: Session = Depends(get_db),
    bank_detail_in: schemas.BankDetailCreate,
    
) -> BankDetail:
    bank_detail_obj = bank_detail.get_by_field(db, "account_number", bank_detail_in.account_number)
    if bank_detail_obj:
        raise HTTPException(status_code=400, detail="account_number already exists")
    
    return bank_detail.create(db=db, obj_in=bank_detail_in)

@api_router.get("/staff_bank_detail/", response_model=List[schemas.BankDetailResponse],  tags=["Bank Detail"])
def read_all_staff_bank_detail(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.BankDetailResponse]:
    bank_detail_obj = bank_detail.get_multi_with_model(db, model=BankDetail, skip=skip, limit=limit)
    return bank_detail_obj

@api_router.get("/bank_detail/{id}", response_model=schemas.BankDetailResponse,  tags=["Bank Detail"])
def read_bank_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.BankDetailResponse:
    bank_detail_obj = bank_detail.get_detailed(db=db, model=BankDetail, id=id)
    if not bank_detail_obj:
        raise HTTPException(status_code=404, detail="bank_detail not found")
    return bank_detail_obj

@api_router.put("/bank_detail/{id}", response_model=schemas.BankDetail,  tags=["Bank Detail"])
def update_bank_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    bank_detail_in: schemas.BankDetailUpdate,
    
) -> BankDetail:
    bank_detail_obj = bank_detail.get(db=db, id=id)
    if not bank_detail_obj:
        raise HTTPException(status_code=404, detail="bank_detail not found")
    return bank_detail.update(db=db, db_obj=bank_detail_obj, obj_in=bank_detail_in)

@api_router.delete("/bank_detail/rm/{id}", response_model=schemas.BankDetail,  tags=["Bank Detail"])
def delete_bank_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> BankDetail:
    bank_detail_obj = bank_detail.get(db=db, id=id)
    if not bank_detail_obj:
        raise HTTPException(status_code=404, detail="bank_detail not found")
    return bank_detail.remove(db=db, id=id, force_delete=force_delete)

















#Academic
@api_router.post("/academic/", response_model=schemas.Academic, tags=["Academics"])
def create_academic(
    *,
    db: Session = Depends(get_db),
    academic_in: schemas.AcademicCreate,
    
) -> Academic:
    academic_obj = academic.get_by_field(db, "bio_row_id", academic_in.bio_row_id)
    if academic_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    return academic.create(db=db, obj_in=academic_in)

@api_router.get("/staff_academic/", response_model=List[schemas.AcademicResponse],  tags=["Academics"])
def read_all_staff_academic(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.AcademicResponse]:
    academic_obj = academic.get_multi_with_model(db, model=Academic, skip=skip, limit=limit)
    return academic_obj

@api_router.get("/academic/{id}", response_model=schemas.AcademicResponse,  tags=["Academics"])
def read_academic(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.AcademicResponse:
    academic_obj = academic.get_detailed(db=db, model=Academic, id=id)
    if not academic_obj:
        raise HTTPException(status_code=404, detail="academic not found")
    return academic_obj

@api_router.put("/academic/{id}", response_model=schemas.Academic,  tags=["Academics"])
def update_academic(
    *,
    db: Session = Depends(get_db),
    id: str,
    academic_in: schemas.AcademicUpdate,
    
) -> Academic:
    academic_obj = academic.get(db=db, id=id)
    if not academic_obj:
        raise HTTPException(status_code=404, detail="academic not found")
    return academic.update(db=db, db_obj=academic_obj, obj_in=academic_in)

@api_router.delete("/academic/rm/{id}", response_model=schemas.Academic,  tags=["Academics"])
def delete_academic(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> Academic:
    academic_obj = academic.get(db=db, id=id)
    if not academic_obj:
        raise HTTPException(status_code=404, detail="academic not found")
    return academic.remove(db=db, id=id, force_delete=force_delete)













#Professional
@api_router.post("/professional/", response_model=schemas.Professional, tags=["Professional Details"])
def create_professional(
    *,
    db: Session = Depends(get_db),
    professional_in: schemas.ProfessionalCreate,
    
) -> Professional:
    professional_obj = professional.get_by_field(db, "bio_row_id", professional_in.bio_row_id)
    if professional_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    return professional.create(db=db, obj_in=professional_in)

@api_router.get("/staff_professional/", response_model=List[schemas.ProfessionalResponse],  tags=["Professional Details"])
def read_all_staff_professional(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.ProfessionalResponse]:
    professional_obj = professional.get_multi_with_model(db, model=Professional, skip=skip, limit=limit)
    return professional_obj

@api_router.get("/professional/{id}", response_model=schemas.ProfessionalResponse,  tags=["Professional Details"])
def read_professional(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.ProfessionalResponse:
    professional_obj = professional.get_detailed(db=db, model=Professional, id=id)
    if not professional_obj:
        raise HTTPException(status_code=404, detail="professional not found")
    return professional_obj

@api_router.put("/professional/{id}", response_model=schemas.Professional,  tags=["Professional Details"])
def update_professional(
    *,
    db: Session = Depends(get_db),
    id: str,
    professional_in: schemas.ProfessionalUpdate,
    
) -> Professional:
    professional_obj = professional.get(db=db, id=id)
    if not professional_obj:
        raise HTTPException(status_code=404, detail="professional not found")
    return professional.update(db=db, db_obj=professional_obj, obj_in=professional_in)

@api_router.delete("/professional/rm/{id}", response_model=schemas.Professional,  tags=["Professional Details"])
def delete_professional(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> Professional:
    professional_obj = professional.get(db=db, id=id)
    if not professional_obj:
        raise HTTPException(status_code=404, detail="professional not found")
    return professional.remove(db=db, id=id, force_delete=force_delete)












#Qualification
@api_router.post("/qualification/", response_model=schemas.Qualification, tags=["Qualification"])
def create_qualification(
    *,
    db: Session = Depends(get_db),
    qualification_in: schemas.QualificationCreate,
    
) -> Qualification:
    qualification_obj = qualification.get_by_field(db, "bio_row_id", qualification_in.bio_row_id)
    if qualification_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    qualification_obj = qualification.get_by_field(db, "academic_qualification_id", qualification_in.academic_qualification_id)
    if qualification_obj:
        raise HTTPException(status_code=400, detail="Academic Qualification already exists")
    
    qualification_obj = qualification.get_by_field(db, "professional_qualification_id", qualification_in.professional_qualification_id)
    if qualification_obj:
        raise HTTPException(status_code=400, detail="Professional  Qualification already exists")
    
    return qualification.create(db=db, obj_in=qualification_in)

@api_router.get("/staff_qualification/", response_model=List[schemas.QualificationResponse],  tags=["Qualification"])
def read_all_staff_qualification(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.QualificationResponse]:
    qualification_obj = qualification.get_multi_with_model(db, model=Qualification, skip=skip, limit=limit)
    return qualification_obj

@api_router.get("/qualification/{id}", response_model=schemas.QualificationResponse,  tags=["Qualification"])
def read_qualification(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.QualificationResponse:
    # qualification_obj = qualification.get(db=db, id=id)
    qualification_obj = qualification.get_detailed(db=db, model=Qualification, id=id)

    if not qualification_obj:
        raise HTTPException(status_code=404, detail="qualification not found")
   
    return qualification_obj #profile


@api_router.put("/qualification/{id}", response_model=schemas.Qualification,  tags=["Qualification"])
def update_qualification(
    *,
    db: Session = Depends(get_db),
    id: str,
    qualification_in: schemas.QualificationUpdate,
    
) -> Qualification:
    qualification_obj = qualification.get(db=db, id=id)
    if not qualification_obj:
        raise HTTPException(status_code=404, detail="qualification not found")
    return qualification.update(db=db, db_obj=qualification_obj, obj_in=qualification_in)

@api_router.delete("/qualification/rm/{id}", response_model=schemas.Qualification,  tags=["Qualification"])
def delete_qualification(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> Qualification:
    qualification_obj = qualification.get(db=db, id=id)
    if not qualification_obj:
        raise HTTPException(status_code=404, detail="qualification not found")
    return qualification.remove(db=db, id=id, force_delete=force_delete)












#EmploymentHistory
@api_router.post("/employment_history/", response_model=schemas.EmploymentHistory, tags=["Employment History"])
def create_employment_history(
    *,
    db: Session = Depends(get_db),
    employment_history_in: schemas.EmploymentHistoryCreate,
    
) -> EmploymentHistory:
    employment_history_obj = employment_history.get_by_field(db, "bio_row_id", employment_history_in.bio_row_id)
    if employment_history_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    return employment_history.create(db=db, obj_in=employment_history_in)

@api_router.get("/staff_employment_history/", response_model=List[schemas.EmploymentHistoryResponse],  tags=["Employment History"])
def read_all_staff_employment_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.EmploymentHistoryResponse]:
    employment_history_obj = employment_history.get_multi_with_model(db, model=EmploymentHistory, skip=skip, limit=limit)
    return employment_history_obj

@api_router.get("/employment_history/{id}", response_model=schemas.EmploymentHistory,  tags=["Employment History"])
def read_employment_history(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.EmploymentHistoryResponse:
    employment_history_obj = employment_history.get_detailed(db=db, model=EmploymentHistory, id=id)
    if not employment_history_obj:
        raise HTTPException(status_code=404, detail="employment_history not found")
    return employment_history_obj

@api_router.put("/employment_history/{id}", response_model=schemas.EmploymentHistory,  tags=["Employment History"])
def update_employment_history(
    *,
    db: Session = Depends(get_db),
    id: str,
    employment_history_in: schemas.EmploymentHistoryUpdate,
    
) -> EmploymentHistory:
    employment_history_obj = employment_history.get(db=db, id=id)
    if not employment_history_obj:
        raise HTTPException(status_code=404, detail="employment_history not found")
    return employment_history.update(db=db, db_obj=employment_history_obj, obj_in=employment_history_in)

@api_router.delete("/employment_history/rm/{id}", response_model=schemas.EmploymentHistory,  tags=["Employment History"])
def delete_employment_history(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> EmploymentHistory:
    employment_history_obj = employment_history.get(db=db, id=id)
    if not employment_history_obj:
        raise HTTPException(status_code=404, detail="employment_history not found")
    return employment_history.remove(db=db, id=id, force_delete=force_delete)














#FamilyInfo
@api_router.post("/family_info/", response_model=schemas.FamilyInfo, tags=["Family Info"])
def create_family_info(
    *,
    db: Session = Depends(get_db),
    family_info_in: schemas.FamilyInfoCreate,
    
) -> FamilyInfo:
    family_info_obj = family_info.get_by_field(db, "bio_row_id", family_info_in.bio_row_id)
    if family_info_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    family_info_obj = family_info.get_by_field(db, "phone_number", family_info_in.phone_number)
    if family_info_obj:
        raise HTTPException(status_code=400, detail="Phone Number already exists")
    
    family_info_obj = family_info.get_by_field(db, "fathers_contact", family_info_in.fathers_contact)
    if family_info_obj:
        raise HTTPException(status_code=400, detail="Fathers Contact already exists")
    
    family_info_obj = family_info.get_by_field(db, "mothers_contact", family_info_in.mothers_contact)
    if family_info_obj:
        raise HTTPException(status_code=400, detail="Mothers Contact already exists")
    
    return family_info.create(db=db, obj_in=family_info_in)

@api_router.get("/staff_family_info/", response_model=List[schemas.FamilyInfoResponse],  tags=["Family Info"])
def read_all_staff_family_info(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.FamilyInfoResponse]:
    family_info_obj = family_info.get_multi_with_model(db, model=FamilyInfo, skip=skip, limit=limit)
    return family_info_obj

@api_router.get("/family_info/{id}", response_model=schemas.FamilyInfoResponse,  tags=["Family Info"])
def read_family_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.FamilyInfoResponse:
    family_info_obj = family_info.get_detailed(db=db, model=FamilyInfo, id=id)
    if not family_info_obj:
        raise HTTPException(status_code=404, detail="family_info not found")
    return family_info_obj

@api_router.put("/family_info/{id}", response_model=schemas.FamilyInfo,  tags=["Family Info"])
def update_family_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    family_info_in: schemas.FamilyInfoUpdate,
    
) -> FamilyInfo:
    family_info_obj = family_info.get(db=db, id=id)
    if not family_info_obj:
        raise HTTPException(status_code=404, detail="family_info not found")
    return family_info.update(db=db, db_obj=family_info_obj, obj_in=family_info_in)

@api_router.delete("/family_info/rm/{id}", response_model=schemas.FamilyInfo,  tags=["Family Info"])
def delete_family_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> FamilyInfo:
    family_info_obj = family_info.get(db=db, id=id)
    if not family_info_obj:
        raise HTTPException(status_code=404, detail="family_info not found")
    return family_info.remove(db=db, id=id, force_delete=force_delete)
















#EmergencyContact
@api_router.post("/emergency_contact/", response_model=schemas.EmergencyContact, tags=["Emergency Contact"])
def create_emergency_contact(
    *,
    db: Session = Depends(get_db),
    emergency_contact_in: schemas.EmergencyContactCreate,
    
) -> EmergencyContact:
    emergency_contact_obj = emergency_contact.get_by_field(db, "bio_row_id", emergency_contact_in.bio_row_id)
    if emergency_contact_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    emergency_contact_obj = emergency_contact.get_by_field(db, "phone_number", emergency_contact_in.phone_number)
    if emergency_contact_obj:
        raise HTTPException(status_code=400, detail="Phone Number already exists")
    
    emergency_contact_obj = emergency_contact.get_by_field(db, "email", emergency_contact_in.email)
    if emergency_contact_obj:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return emergency_contact.create(db=db, obj_in=emergency_contact_in)

@api_router.get("/staff_emergency_contact/", response_model=List[schemas.EmergencyContactResponse],  tags=["Emergency Contact"])
def read_all_staff_emergency_contact(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.EmergencyContactResponse]:
    emergency_contact_obj = emergency_contact.get_multi_with_model(db, model=EmergencyContact, skip=skip, limit=limit)
    return emergency_contact_obj

@api_router.get("/emergency_contact/{id}", response_model=schemas.EmergencyContactResponse,  tags=["Emergency Contact"])
def read_emergency_contact(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.EmergencyContactResponse:
    emergency_contact_obj = emergency_contact.get_detailed(db=db, model=EmergencyContact, id=id)
    if not emergency_contact_obj:
        raise HTTPException(status_code=404, detail="emergency_contact not found")
    return emergency_contact_obj

@api_router.put("/emergency_contact/{id}", response_model=schemas.EmergencyContact,  tags=["Emergency Contact"])
def update_emergency_contact(
    *,
    db: Session = Depends(get_db),
    id: str,
    emergency_contact_in: schemas.EmergencyContactUpdate,
    
) -> EmergencyContact:
    emergency_contact_obj = emergency_contact.get(db=db, id=id)
    if not emergency_contact_obj:
        raise HTTPException(status_code=404, detail="emergency_contact not found")
    return emergency_contact.update(db=db, db_obj=emergency_contact_obj, obj_in=emergency_contact_in)

@api_router.delete("/emergency_contact/rm/{id}", response_model=schemas.EmergencyContact,  tags=["Emergency Contact"])
def delete_emergency_contact(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> EmergencyContact:
    emergency_contact_obj = emergency_contact.get(db=db, id=id)
    if not emergency_contact_obj:
        raise HTTPException(status_code=404, detail="emergency_contact not found")
    return emergency_contact.remove(db=db, id=id, force_delete=force_delete)













#NextOfKin
@api_router.post("/next_of_kin/", response_model=schemas.NextOfKin, tags=["Next Of Kin"])
def create_next_of_kin(
    *,
    db: Session = Depends(get_db),
    next_of_kin_in: schemas.NextOfKinCreate,
    
) -> NextOfKin:
    next_of_kin_obj = next_of_kin.get_by_field(db, "bio_row_id", next_of_kin_in.bio_row_id)
    if next_of_kin_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    next_of_kin_obj = next_of_kin.get_by_field(db, "phone", next_of_kin_in.phone)
    if next_of_kin_obj:
        raise HTTPException(status_code=400, detail="Phone Number already exists")
    
    next_of_kin_obj = next_of_kin.get_by_field(db, "email", next_of_kin_in.email)
    if next_of_kin_obj:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return next_of_kin.create(db=db, obj_in=next_of_kin_in)

@api_router.get("/staff_next_of_kin/", response_model=List[schemas.NextOfKinResponse],  tags=["Next Of Kin"])
def read_all_staff_next_of_kin(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    
) -> List[schemas.NextOfKinResponse]:
    next_of_kin_obj = next_of_kin.get_multi_with_model(db, model=NextOfKin, skip=skip, limit=limit)
    return next_of_kin_obj

@api_router.get("/next_of_kin/{id}", response_model=schemas.NextOfKinResponse,  tags=["Next Of Kin"])
def read_next_of_kin(
    *,
    db: Session = Depends(get_db),
    id: str,
    
) -> schemas.NextOfKinResponse:
    next_of_kin_obj = next_of_kin.get_detailed(db=db, model=NextOfKin, id=id)
    if not next_of_kin_obj:
        raise HTTPException(status_code=404, detail="next_of_kin not found")
    return next_of_kin_obj

@api_router.put("/next_of_kin/{id}", response_model=schemas.NextOfKin,  tags=["Next Of Kin"])
def update_next_of_kin(
    *,
    db: Session = Depends(get_db),
    id: str,
    next_of_kin_in: schemas.NextOfKinUpdate,
    
) -> NextOfKin:
    next_of_kin_obj = next_of_kin.get(db=db, id=id)
    if not next_of_kin_obj:
        raise HTTPException(status_code=404, detail="next_of_kin not found")
    return next_of_kin.update(db=db, db_obj=next_of_kin_obj, obj_in=next_of_kin_in)

@api_router.delete("/next_of_kin/rm/{id}", response_model=schemas.NextOfKin,  tags=["Next Of Kin"])
def delete_next_of_kin(
    *,
    db: Session = Depends(get_db),
    id: str,
    force_delete: bool = Query(False)  # Default is False, allowing normal delete
) -> NextOfKin:
    next_of_kin_obj = next_of_kin.get(db=db, id=id)
    if not next_of_kin_obj:
        raise HTTPException(status_code=404, detail="next_of_kin not found")
    return next_of_kin.remove(db=db, id=id, force_delete=force_delete)











from tempfile import NamedTemporaryFile, TemporaryDirectory
import logging

#from .history.app.schemas_20240814124601 import QualificationResponse

logger = logging.getLogger(__name__)

@api_router.get("/download-form/{bio_data_id}", response_description="Generate PDF for BioData", tags=["Download Records"])
def generate_records_data_pdf(bio_data_id: str, db: Session = Depends(get_db)):
    bio_data = db.query(BioData).filter(BioData.id == bio_data_id).first()
    if not bio_data:
        raise HTTPException(status_code=404, detail="BioData not found")

    trademark = db.query(Trademark).first()
    if not trademark:
        raise HTTPException(status_code=404, detail="Trademark not found")

    declarations = db.query(Declaration).filter(Declaration.bio_row_id == bio_data.id).all()
    if not declarations:
        raise HTTPException(status_code=404, detail="Declarations not found")

    academics = db.query(Academic).filter(Academic.bio_row_id == bio_data.id).all()
    if not academics:
        raise HTTPException(status_code=404, detail="Academics not found")

    professionals = db.query(Professional).filter(Professional.bio_row_id == bio_data.id).all()
    if not professionals:
        raise HTTPException(status_code=404, detail="Professionals not found")
    
    history_of_employment = db.query(EmploymentHistory).filter(EmploymentHistory.bio_row_id == bio_data.id).all()
    if not history_of_employment:
        raise HTTPException(status_code=404, detail="Employment History not found")
    

    emergency_contacts = db.query(EmergencyContact).filter(EmergencyContact.bio_row_id == bio_data.id).all()
    if not emergency_contacts:
        raise HTTPException(status_code=404, detail="Emergency Contact not found")
    
    next_of_kins = db.query(NextOfKin).filter(NextOfKin.bio_row_id == bio_data.id).all()
    if not next_of_kins:
        raise HTTPException(status_code=404, detail="Next of Kin not found")

    # Fetch related names for employment details
    grade_name = db.query(Grade.name).filter(Grade.id == bio_data.employment_detail.grade_on_current_appointment_id).scalar()
    directorate_name = db.query(Directorate.name).filter(Directorate.id == bio_data.employment_detail.directorate_id).scalar()
    employment_type_name = db.query(EmploymentType.name).filter(EmploymentType.id == bio_data.employment_detail.employment_type_id).scalar()
    staff_category_name = db.query(StaffCategory.category).filter(StaffCategory.id == bio_data.employment_detail.staff_category_id).scalar()
    
    # Create temporary file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        file_path = tmp_file.name
        #file_path = f"/uploads/images/bio_data_{bio_data_id}.pdf"
    try:
        #path = generate_pdf_for_bio_data(bio_data, trademark, declarations, academics, professionals,history_of_employment ,emergency_contacts, next_of_kins, file_path)
        print("biodata:: ",bio_data)
        path = generate_pdf_for_bio_data(
            bio_data, trademark, declarations, academics, professionals, 
            history_of_employment, emergency_contacts, next_of_kins, 
            grade_name, directorate_name, employment_type_name, staff_category_name, 
            file_path
        )
        print("path: ", path)
        if not path or not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Failed to generate PDF file")
        
        print("file_path in api: ", file_path)
        return FileResponse(path, filename=f"bio_data_{bio_data_id}.pdf", media_type='application/pdf')
    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}")
        raise HTTPException(status_code=404, detail="PDF file not found")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF.")
    finally:
        # Clean up the file after it's generated and served
        if os.path.exists(file_path):
            os.remove(file_path)


