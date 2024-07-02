from datetime import date
from fastapi import APIRouter, Depends, Form, HTTPException, Query, status, UploadFile, File
from pydantic import EmailStr
from sqlalchemy.orm import Session
from database.db_session import get_db
import schemas
from models import (BioData, EmploymentDetail, BankDetail, Academic, Professional, 
                        Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, 
                        NextOfKin, Declaration, StaffCategory, Centre, User, Directorate, Grade, EmploymentType, Trademark)
from crud import (bio_data, declaration, 
                  user, trademark)

from typing import List, Optional, Type,  Union, Dict, Any
from fastapi.responses import FileResponse
import os
from crud import generate_pdf_for_bio_data
import crud
from _crud import (centre, employment_type, grade, directorate, staff_category, bank_detail, emergency_contact, employment_detail, employment_history, 
                  next_of_kin, family_info, academic, professional, qualification)

from auth import current_active_user, current_active_admin, current_active_admin_user
from uuid import UUID
import tempfile



# List of all models
all_models = [
    Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, 
    BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]


bio_data_related_models  = [
    EmploymentDetail, BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]


api_router = APIRouter(prefix="/api")


@api_router.get("/search/", response_model=Dict[str, List[Dict[str, Any]]], tags=["Search Space"])
def search(search_string: str, db: Session = Depends(get_db)):
    results = crud.search_all(db, search_string, all_models)
    return results

#Business Brand
@api_router.post("/logo/", response_model=schemas.Trademark, tags=["Business Brand"])
def create_logo(
    *,
    db: Session = Depends(get_db),
    trade_in: schemas.TrademarkCreate = Depends(),
    left_logo: UploadFile = File(None),
    right_logo: UploadFile = File(None),
    current_user: User = Depends(current_active_admin)
) -> Trademark:
    logo_obj = trademark.get_by_field(db, "name", trade_in.name)
    if logo_obj:
        raise HTTPException(status_code=400, detail="Business Info already exists")
    return trademark.create(db=db, obj_in=trade_in, file=left_logo, file2=right_logo)

@api_router.get("/logo/get/{id}", response_model=schemas.Trademark,  tags=["Business Brand"])
def read_logo(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Trademark:
    trademark_obj = trademark.get(db=db, id=id)
    if not trademark_obj:
        raise HTTPException(status_code=404, detail="Logo not found")
    return trademark_obj

@api_router.put("/logo/update/{id}", response_model=schemas.Trademark,  tags=["Business Brand"])
def update_logo(
    *,
    db: Session = Depends(get_db),
    id: str,
    trademark_in: schemas.TrademarkUpdate,
    left_logo: UploadFile = File(None),
    right_logo: UploadFile = File(None),
    current_user: User = Depends(current_active_admin)
) -> Trademark:
    logo_obj = trademark.get(db=db, id=id)
    if not logo_obj:
        raise HTTPException(status_code=404, detail="logo not found")
    return trademark.update(db=db, db_obj=logo_obj, obj_in=trademark_in, file=left_logo, file2=right_logo)





#Centre
@api_router.post("/centres/", response_model=schemas.Centre, tags=["Centre"])
def create_centre(
    *,
    db: Session = Depends(get_db),
    centre_in: schemas.CentreCreate,
    current_user: User = Depends(current_active_admin)
) -> Centre:
    centre_obj = centre.get_by_field(db, "location", centre_in.location)
    if centre_obj:
        raise HTTPException(status_code=400, detail="Centre already exists")
    return centre.create(db=db, obj_in=centre_in)

@api_router.get("/centres/", response_model=List[schemas.Centre],  tags=["Centre"])
def read_centres(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[Centre]:
    centres = centre.get_multi(db, skip=skip, limit=limit)
    return centres

@api_router.get("/centres/{id}", response_model=schemas.Centre,  tags=["Centre"])
def read_centre(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Centre:
    centre_obj = centre.get(db=db, id=id)
    if not centre_obj:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre_obj

@api_router.put("/centres/{id}", response_model=schemas.Centre,  tags=["Centre"])
def update_centre(
    *,
    db: Session = Depends(get_db),
    id: str,
    centre_in: schemas.CentreUpdate,
    current_user: User = Depends(current_active_admin)
) -> Centre:
    centre_obj = centre.get(db=db, id=id)
    if not centre_obj:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre.update(db=db, db_obj=centre_obj, obj_in=centre_in)

@api_router.delete("/centres/{id}", response_model=schemas.Centre,  tags=["Centre"])
def delete_centre(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin)
) -> Centre:
    centre_obj = centre.get(db=db, id=id)
    if not centre_obj:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre.remove(db=db, id=id)


#Directorate
@api_router.post("/directorate/", response_model=schemas.Directorate, tags=["Directorate"])
def create_directorate(
    *,
    db: Session = Depends(get_db),
    directorate_in: schemas.DirectorateCreate,
    current_user: User = Depends(current_active_admin)
) -> Directorate:
    directorate_obj = directorate.get_by_field(db, "name", directorate_in.name)
    if directorate_obj:
        raise HTTPException(status_code=400, detail="directorate already exists")
    return directorate.create(db=db, obj_in=directorate_in)

@api_router.get("/directorates/", response_model=List[schemas.Directorate],  tags=["Directorate"])
def read_directorates(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[Directorate]:
    directorate_obj = directorate.get_multi(db, skip=skip, limit=limit)
    return directorate_obj

@api_router.get("/directorate/{id}", response_model=schemas.Directorate,  tags=["Directorate"])
def read_directorate(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Directorate:
    directorate_obj = directorate.get(db=db, id=id)
    if not directorate_obj:
        raise HTTPException(status_code=404, detail="directorate not found")
    return directorate_obj

@api_router.put("/directorate/{id}", response_model=schemas.Directorate,  tags=["Directorate"])
def update_directorate(
    *,
    db: Session = Depends(get_db),
    id: str,
    directorate_in: schemas.DirectorateUpdate,
    current_user: User = Depends(current_active_admin)
) -> Directorate:
    directorate_obj = directorate.get(db=db, id=id)
    if not directorate_obj:
        raise HTTPException(status_code=404, detail="directorate not found")
    return directorate.update(db=db, db_obj=directorate_obj, obj_in=directorate_in)

@api_router.delete("/directorate/{id}", response_model=schemas.Directorate,  tags=["Directorate"])
def delete_directorate(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Directorate:
    directorate_obj = directorate.get(db=db, id=id)
    if not directorate_obj:
        raise HTTPException(status_code=404, detail="directorate not found")
    return directorate.remove(db=db, id=id)


#Grade
@api_router.post("/grade/", response_model=schemas.Grade, tags=["Grade"])
def create_grade(
    *,
    db: Session = Depends(get_db),
    grade_in: schemas.GradeCreate,
    current_user: User = Depends(current_active_admin)
) -> Grade:
    grade_obj = grade.get_by_field(db, "name", grade_in.name)
    if grade_obj:
        raise HTTPException(status_code=400, detail="grade already exists")
    return grade.create(db=db, obj_in=grade_in)

@api_router.get("/grades/", response_model=List[schemas.Grade],  tags=["Grade"])
def read_grades(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[Grade]:
    grade_obj = grade.get_multi(db, skip=skip, limit=limit)
    return grade_obj

@api_router.get("/grade/{id}", response_model=schemas.Grade,  tags=["Grade"])
def read_grade(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
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
    current_user: User = Depends(current_active_admin)
) -> Grade:
    grade_obj = grade.get(db=db, id=id)
    if not grade_obj:
        raise HTTPException(status_code=404, detail="grade not found")
    return grade.update(db=db, db_obj=grade_obj, obj_in=grade_in)

@api_router.delete("/grade/{id}", response_model=schemas.Grade,  tags=["Grade"])
def delete_grade(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin)
) -> Grade:
    grade_obj = grade.get(db=db, id=id)
    if not grade_obj:
        raise HTTPException(status_code=404, detail="grade not found")
    return grade.remove(db=db, id=id)


#Employment Type
@api_router.post("/employment_type/", response_model=schemas.EmploymentType, tags=["Employment Type"])
def create_employment_type(
    *,
    db: Session = Depends(get_db),
    employment_type_in: schemas.EmploymentTypeCreate,
    current_user: User = Depends(current_active_admin)
) -> EmploymentType:
    employment_type_obj = employment_type.get_by_field(db, "name", employment_type_in.name)
    if employment_type_obj:
        raise HTTPException(status_code=400, detail="employment_type already exists")
    return employment_type.create(db=db, obj_in=employment_type_in)

@api_router.get("/employment_types/", response_model=List[schemas.EmploymentType],  tags=["Employment Type"])
def read_employment_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[EmploymentType]:
    employment_type_obj = employment_type.get_multi(db, skip=skip, limit=limit)
    return employment_type_obj

@api_router.get("/employment_type/{id}", response_model=schemas.EmploymentType,  tags=["Employment Type"])
def read_employment_type(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentType:
    employment_type_obj = employment_type.get(db=db, id=id)
    if not employment_type_obj:
        raise HTTPException(status_code=404, detail="employment_type not found")
    return employment_type_obj

@api_router.put("/employment_type/{id}", response_model=schemas.EmploymentType,  tags=["Employment Type"])
def update_employment_type(
    *,
    db: Session = Depends(get_db),
    id: str,
    employment_type_in: schemas.EmploymentTypeUpdate,
    current_user: User = Depends(current_active_admin)
) -> EmploymentType:
    employment_type_obj = employment_type.get(db=db, id=id)
    if not employment_type_obj:
        raise HTTPException(status_code=404, detail="employment_type not found")
    return employment_type.update(db=db, db_obj=employment_type_obj, obj_in=employment_type_in)

@api_router.delete("/employment_type/{id}", response_model=schemas.EmploymentType,  tags=["Employment Type"])
def delete_employment_type(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin)
) -> EmploymentType:
    employment_type_obj = employment_type.get(db=db, id=id)
    if not employment_type_obj:
        raise HTTPException(status_code=404, detail="employment_type not found")
    return employment_type.remove(db=db, id=id)


#Staff Category
@api_router.post("/staff_category/", response_model=schemas.StaffCategory, tags=["Staff Category"])
def create_staff_category(
    *,
    db: Session = Depends(get_db),
    staff_category_in: schemas.StaffCategoryCreate,
    current_user: User = Depends(current_active_admin)
) -> StaffCategory:
    staff_category_obj = staff_category.get_by_field(db, "category", staff_category_in.category)
    if staff_category_obj:
        raise HTTPException(status_code=400, detail="staff_category already exists")
    return staff_category.create(db=db, obj_in=staff_category_in)

@api_router.get("/staff_categories/", response_model=List[schemas.StaffCategory],  tags=["Staff Category"])
def read_staff_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[StaffCategory]:
    staff_category_obj = staff_category.get_multi(db, skip=skip, limit=limit)
    return staff_category_obj

@api_router.get("/staff_category/{id}", response_model=schemas.StaffCategory,  tags=["Staff Category"])
def read_staff_category(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
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
    current_user: User = Depends(current_active_admin)
) -> StaffCategory:
    staff_category_obj = staff_category.get(db=db, id=id)
    if not staff_category_obj:
        raise HTTPException(status_code=404, detail="staff_category not found")
    return staff_category.update(db=db, db_obj=staff_category_obj, obj_in=staff_category_in)

@api_router.delete("/staff_category/{id}", response_model=schemas.StaffCategory,  tags=["Staff Category"])
def delete_staff_category(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin)
) -> StaffCategory:
    staff_category_obj = staff_category.get(db=db, id=id)
    if not staff_category_obj:
        raise HTTPException(status_code=404, detail="staff_category not found")
    return staff_category.remove(db=db, id=id)


#BioData
@api_router.post("/bio_data/", response_model=schemas.BioData, tags=["BioData"])
def create_bio_data(
    *,
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
    current_user: User = Depends(current_active_admin_user)
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
    
    bio_data_in = schemas.BioDataCreate(
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
    #files = {"image_col": file}
    return bio_data.create(db=db, obj_in=bio_data_in, files=files)

@api_router.get("/staff_bio_data/", response_model=List[schemas.BioData], tags=["BioData"])
def read__staff_bio_data(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin)
) -> List[BioData]:
    bio_data_list = bio_data.get_multi(db, skip=skip, limit=limit)
    return bio_data_list

@api_router.get("/bio_data/{id}", response_model=schemas.BioData, tags=["BioData"])
def read_bio_data(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
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
    current_user: User = Depends(current_active_admin_user)
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





@api_router.delete("/bio_data/{id}", response_model=schemas.BioData,  tags=["BioData"])
def delete_bio_data(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> BioData:
    bio_data_obj = bio_data.get(db=db, id=id)
    if not bio_data_obj:
        raise HTTPException(status_code=404, detail="bio_data not found")
    return bio_data.remove(db=db, id=id)



#users
@api_router.post("/user", response_model=schemas.User,  tags=["Users"], status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: User = Depends(current_active_admin)):
    return crud.create_user(db=db, user=user)

@api_router.get("/user/get/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(current_active_admin_user)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@api_router.get("/get/allusers", tags=["Users"])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(current_active_admin)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@api_router.put("/user/update/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: UUID, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(current_active_admin_user)):
    return crud.update_user(db=db, user_id=user_id, user_update=user_update)



@api_router.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(current_active_admin_user)):
    db_user = user.remove(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return "Data deleted successfully"






@api_router.post("/declaration/", response_model=schemas.Declaration, tags=["Declaration"])
def create_declaration(
    *,
    db: Session = Depends(get_db),
    #declaration_in: schemas.DeclarationCreate,
    bio_row_id: Optional[str] = Form(None),
    status: Optional[bool] = Form(None),
    declaration_date: Optional[date] = Form(None),
    reps_signature: UploadFile = File(None),
    employees_signature: UploadFile = File(None),

    current_user: User = Depends(current_active_admin_user)
) -> Any:
    

    declaration_in = schemas.DeclarationCreate(
        bio_row_id = bio_row_id,
        status=status,
        declaration_date=declaration_date
    )

    files = {
        'reps_signature': reps_signature.file.read() if reps_signature else None,
        'employees_signature': employees_signature.file.read() if employees_signature else None
    }

    declaration = crud.declaration.create(db=db, obj_in=declaration_in, files=files)
    return declaration

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
    current_user: User = Depends(current_active_admin_user)
) -> Declaration:
    declarat = crud.declaration.get(db=db, id=id)
    if not declarat:
        raise HTTPException(status_code=404, detail="Declaration not found")

    files = {
        'reps_signature': reps_signature.file.read() if reps_signature else None,
        'employees_signature': employees_signature.file.read() if employees_signature else None
    }

    declaration_in = schemas.DeclarationUpdate(
        bio_row_id=bio_row_id,
        status=status,
        declaration_date=declaration_date
    )

    declaratio = crud.declaration.update(db=db, db_obj=declarat, obj_in=declaration_in, files=files)
    return declaratio

@api_router.delete("/declaration/{id}", response_model=schemas.Declaration, tags=["Declaration"])
def delete_declaration(
    *,
    db: Session = Depends(get_db),
    id: UUID,
    force_delete: bool = Query(False, description="Force delete related data"),
    current_user: User = Depends(current_active_admin_user)
) -> Any:
    if not force_delete:
        # Simulate user prompt by requiring an additional confirmation parameter
        raise HTTPException(status_code=400, detail="Are you sure you want to delete all related data? This action is irreversible. Set force_delete=True to confirm.")
    
    declaration = crud.declaration.remove(db=db, id=id, force_delete=force_delete)
    return declaration




#Employment Deatails
#Staff Category
@api_router.post("/employment_detail/", response_model=schemas.EmploymentDetail, tags=["Employment Detail"])
def create_employment_detail(
    *,
    db: Session = Depends(get_db),
    employment_detail_in: schemas.EmploymentDetailCreate,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentDetail:
    employment_detail_obj = employment_detail.get_by_field(db, "bio_row_id", employment_detail_in.bio_row_id)
    if employment_detail_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    employment_detail_obj = employment_detail.get_by_field(db, "employee_number", employment_detail_in.employee_number)
    if employment_detail_obj:
        raise HTTPException(status_code=400, detail="Employee Number already exists")
    return employment_detail.create(db=db, obj_in=employment_detail_in)

@api_router.get("/staff_employment_detail/", response_model=List[schemas.EmploymentDetail],  tags=["Employment Detail"])
def read_all_staff_employment_detail(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[EmploymentDetail]:
    employment_detail_obj = employment_detail.get_multi(db, skip=skip, limit=limit)
    return employment_detail_obj

@api_router.get("/employment_detail/{id}", response_model=schemas.EmploymentDetail,  tags=["Employment Detail"])
def read_employment_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentDetail:
    employment_detail_obj = employment_detail.get(db=db, id=id)
    if not employment_detail_obj:
        raise HTTPException(status_code=404, detail="employment_detail not found")
    return employment_detail_obj

@api_router.put("/employment_detail/{id}", response_model=schemas.EmploymentDetail,  tags=["Employment Detail"])
def update_employment_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    employment_detail_in: schemas.EmploymentDetailUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentDetail:
    employment_detail_obj = employment_detail.get(db=db, id=id)
    if not employment_detail_obj:
        raise HTTPException(status_code=404, detail="employment_detail not found")
    return employment_detail.update(db=db, db_obj=employment_detail_obj, obj_in=employment_detail_in)

@api_router.delete("/employment_detail/{id}", response_model=schemas.EmploymentDetail,  tags=["Employment Detail"])
def delete_employment_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentDetail:
    employment_detail_obj = employment_detail.get(db=db, id=id)
    if not employment_detail_obj:
        raise HTTPException(status_code=404, detail="employment_detail not found")
    return employment_detail.remove(db=db, id=id)


















#BankDetail
@api_router.post("/bank_detail/", response_model=schemas.BankDetail, tags=["Bank Detail"])
def create_bank_detail(
    *,
    db: Session = Depends(get_db),
    bank_detail_in: schemas.BankDetailCreate,
    current_user: User = Depends(current_active_admin_user)
) -> BankDetail:
    bank_detail_obj = bank_detail.get_by_field(db, "account_number", bank_detail_in.account_number)
    if bank_detail_obj:
        raise HTTPException(status_code=400, detail="account_number already exists")
    
    return bank_detail.create(db=db, obj_in=bank_detail_in)

@api_router.get("/staff_bank_detail/", response_model=List[schemas.BankDetail],  tags=["Bank Detail"])
def read_all_staff_bank_detail(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[BankDetail]:
    bank_detail_obj = bank_detail.get_multi(db, skip=skip, limit=limit)
    return bank_detail_obj

@api_router.get("/bank_detail/{id}", response_model=schemas.BankDetail,  tags=["Bank Detail"])
def read_bank_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> BankDetail:
    bank_detail_obj = bank_detail.get(db=db, id=id)
    if not bank_detail_obj:
        raise HTTPException(status_code=404, detail="bank_detail not found")
    return bank_detail_obj

@api_router.put("/bank_detail/{id}", response_model=schemas.BankDetail,  tags=["Bank Detail"])
def update_bank_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    bank_detail_in: schemas.BankDetailUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> BankDetail:
    bank_detail_obj = bank_detail.get(db=db, id=id)
    if not bank_detail_obj:
        raise HTTPException(status_code=404, detail="bank_detail not found")
    return bank_detail.update(db=db, db_obj=bank_detail_obj, obj_in=bank_detail_in)

@api_router.delete("/bank_detail/{id}", response_model=schemas.BankDetail,  tags=["Bank Detail"])
def delete_bank_detail(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> BankDetail:
    bank_detail_obj = bank_detail.get(db=db, id=id)
    if not bank_detail_obj:
        raise HTTPException(status_code=404, detail="bank_detail not found")
    return bank_detail.remove(db=db, id=id)

















#Academic
@api_router.post("/academic/", response_model=schemas.Academic, tags=["Academics"])
def create_academic(
    *,
    db: Session = Depends(get_db),
    academic_in: schemas.AcademicCreate,
    current_user: User = Depends(current_active_admin_user)
) -> Academic:
    academic_obj = academic.get_by_field(db, "bio_row_id", academic_in.bio_row_id)
    if academic_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    return academic.create(db=db, obj_in=academic_in)

@api_router.get("/staff_academic/", response_model=List[schemas.Academic],  tags=["Academics"])
def read_all_staff_academic(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[Academic]:
    academic_obj = academic.get_multi(db, skip=skip, limit=limit)
    return academic_obj

@api_router.get("/academic/{id}", response_model=schemas.Academic,  tags=["Academics"])
def read_academic(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Academic:
    academic_obj = academic.get(db=db, id=id)
    if not academic_obj:
        raise HTTPException(status_code=404, detail="academic not found")
    return academic_obj

@api_router.put("/academic/{id}", response_model=schemas.Academic,  tags=["Academics"])
def update_academic(
    *,
    db: Session = Depends(get_db),
    id: str,
    academic_in: schemas.AcademicUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> Academic:
    academic_obj = academic.get(db=db, id=id)
    if not academic_obj:
        raise HTTPException(status_code=404, detail="academic not found")
    return academic.update(db=db, db_obj=academic_obj, obj_in=academic_in)

@api_router.delete("/academic/{id}", response_model=schemas.Academic,  tags=["Academics"])
def delete_academic(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Academic:
    academic_obj = academic.get(db=db, id=id)
    if not academic_obj:
        raise HTTPException(status_code=404, detail="academic not found")
    return academic.remove(db=db, id=id)













#Professional
@api_router.post("/professional/", response_model=schemas.Professional, tags=["Professional Details"])
def create_professional(
    *,
    db: Session = Depends(get_db),
    professional_in: schemas.ProfessionalCreate,
    current_user: User = Depends(current_active_admin_user)
) -> Professional:
    professional_obj = professional.get_by_field(db, "bio_row_id", professional_in.bio_row_id)
    if professional_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    return professional.create(db=db, obj_in=professional_in)

@api_router.get("/staff_professional/", response_model=List[schemas.Professional],  tags=["Professional Details"])
def read_all_staff_professional(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[Professional]:
    professional_obj = professional.get_multi(db, skip=skip, limit=limit)
    return professional_obj

@api_router.get("/professional/{id}", response_model=schemas.Professional,  tags=["Professional Details"])
def read_professional(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Professional:
    professional_obj = professional.get(db=db, id=id)
    if not professional_obj:
        raise HTTPException(status_code=404, detail="professional not found")
    return professional_obj

@api_router.put("/professional/{id}", response_model=schemas.Professional,  tags=["Professional Details"])
def update_professional(
    *,
    db: Session = Depends(get_db),
    id: str,
    professional_in: schemas.ProfessionalUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> Professional:
    professional_obj = professional.get(db=db, id=id)
    if not professional_obj:
        raise HTTPException(status_code=404, detail="professional not found")
    return professional.update(db=db, db_obj=professional_obj, obj_in=professional_in)

@api_router.delete("/professional/{id}", response_model=schemas.Professional,  tags=["Professional Details"])
def delete_professional(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Professional:
    professional_obj = professional.get(db=db, id=id)
    if not professional_obj:
        raise HTTPException(status_code=404, detail="professional not found")
    return professional.remove(db=db, id=id)












#Qualification
@api_router.post("/qualification/", response_model=schemas.Qualification, tags=["Qualification"])
def create_qualification(
    *,
    db: Session = Depends(get_db),
    qualification_in: schemas.QualificationCreate,
    current_user: User = Depends(current_active_admin_user)
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

@api_router.get("/staff_qualification/", response_model=List[schemas.Qualification],  tags=["Qualification"])
def read_all_staff_qualification(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[Qualification]:
    qualification_obj = qualification.get_multi(db, skip=skip, limit=limit)
    return qualification_obj

@api_router.get("/qualification/{id}", response_model=schemas.Qualification,  tags=["Qualification"])
def read_qualification(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Qualification:
    qualification_obj = qualification.get(db=db, id=id)
    if not qualification_obj:
        raise HTTPException(status_code=404, detail="qualification not found")
    return qualification_obj

@api_router.put("/qualification/{id}", response_model=schemas.Qualification,  tags=["Qualification"])
def update_qualification(
    *,
    db: Session = Depends(get_db),
    id: str,
    qualification_in: schemas.QualificationUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> Qualification:
    qualification_obj = qualification.get(db=db, id=id)
    if not qualification_obj:
        raise HTTPException(status_code=404, detail="qualification not found")
    return qualification.update(db=db, db_obj=qualification_obj, obj_in=qualification_in)

@api_router.delete("/qualification/{id}", response_model=schemas.Qualification,  tags=["Qualification"])
def delete_qualification(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> Qualification:
    qualification_obj = qualification.get(db=db, id=id)
    if not qualification_obj:
        raise HTTPException(status_code=404, detail="qualification not found")
    return qualification.remove(db=db, id=id)












#EmploymentHistory
@api_router.post("/employment_history/", response_model=schemas.EmploymentHistory, tags=["Employment History"])
def create_employment_history(
    *,
    db: Session = Depends(get_db),
    employment_history_in: schemas.EmploymentHistoryCreate,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentHistory:
    employment_history_obj = employment_history.get_by_field(db, "bio_row_id", employment_history_in.bio_row_id)
    if employment_history_obj:
        raise HTTPException(status_code=400, detail="BioData already exists")
    
    return employment_history.create(db=db, obj_in=employment_history_in)

@api_router.get("/staff_employment_history/", response_model=List[schemas.EmploymentHistory],  tags=["Employment History"])
def read_all_staff_employment_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[EmploymentHistory]:
    employment_history_obj = employment_history.get_multi(db, skip=skip, limit=limit)
    return employment_history_obj

@api_router.get("/employment_history/{id}", response_model=schemas.EmploymentHistory,  tags=["Employment History"])
def read_employment_history(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentHistory:
    employment_history_obj = employment_history.get(db=db, id=id)
    if not employment_history_obj:
        raise HTTPException(status_code=404, detail="employment_history not found")
    return employment_history_obj

@api_router.put("/employment_history/{id}", response_model=schemas.EmploymentHistory,  tags=["Employment History"])
def update_employment_history(
    *,
    db: Session = Depends(get_db),
    id: str,
    employment_history_in: schemas.EmploymentHistoryUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentHistory:
    employment_history_obj = employment_history.get(db=db, id=id)
    if not employment_history_obj:
        raise HTTPException(status_code=404, detail="employment_history not found")
    return employment_history.update(db=db, db_obj=employment_history_obj, obj_in=employment_history_in)

@api_router.delete("/employment_history/{id}", response_model=schemas.EmploymentHistory,  tags=["Employment History"])
def delete_employment_history(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> EmploymentHistory:
    employment_history_obj = employment_history.get(db=db, id=id)
    if not employment_history_obj:
        raise HTTPException(status_code=404, detail="employment_history not found")
    return employment_history.remove(db=db, id=id)














#FamilyInfo
@api_router.post("/family_info/", response_model=schemas.FamilyInfo, tags=["Family Info"])
def create_family_info(
    *,
    db: Session = Depends(get_db),
    family_info_in: schemas.FamilyInfoCreate,
    current_user: User = Depends(current_active_admin_user)
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

@api_router.get("/staff_family_info/", response_model=List[schemas.FamilyInfo],  tags=["Family Info"])
def read_all_staff_family_info(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[FamilyInfo]:
    family_info_obj = family_info.get_multi(db, skip=skip, limit=limit)
    return family_info_obj

@api_router.get("/family_info/{id}", response_model=schemas.FamilyInfo,  tags=["Family Info"])
def read_family_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> FamilyInfo:
    family_info_obj = family_info.get(db=db, id=id)
    if not family_info_obj:
        raise HTTPException(status_code=404, detail="family_info not found")
    return family_info_obj

@api_router.put("/family_info/{id}", response_model=schemas.FamilyInfo,  tags=["Family Info"])
def update_family_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    family_info_in: schemas.FamilyInfoUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> FamilyInfo:
    family_info_obj = family_info.get(db=db, id=id)
    if not family_info_obj:
        raise HTTPException(status_code=404, detail="family_info not found")
    return family_info.update(db=db, db_obj=family_info_obj, obj_in=family_info_in)

@api_router.delete("/family_info/{id}", response_model=schemas.FamilyInfo,  tags=["Family Info"])
def delete_family_info(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> FamilyInfo:
    family_info_obj = family_info.get(db=db, id=id)
    if not family_info_obj:
        raise HTTPException(status_code=404, detail="family_info not found")
    return family_info.remove(db=db, id=id)
















#EmergencyContact
@api_router.post("/emergency_contact/", response_model=schemas.EmergencyContact, tags=["Emergency Contact"])
def create_emergency_contact(
    *,
    db: Session = Depends(get_db),
    emergency_contact_in: schemas.EmergencyContactCreate,
    current_user: User = Depends(current_active_admin_user)
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

@api_router.get("/staff_emergency_contact/", response_model=List[schemas.EmergencyContact],  tags=["Emergency Contact"])
def read_all_staff_emergency_contact(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[EmergencyContact]:
    emergency_contact_obj = emergency_contact.get_multi(db, skip=skip, limit=limit)
    return emergency_contact_obj

@api_router.get("/emergency_contact/{id}", response_model=schemas.EmergencyContact,  tags=["Emergency Contact"])
def read_emergency_contact(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> EmergencyContact:
    emergency_contact_obj = emergency_contact.get(db=db, id=id)
    if not emergency_contact_obj:
        raise HTTPException(status_code=404, detail="emergency_contact not found")
    return emergency_contact_obj

@api_router.put("/emergency_contact/{id}", response_model=schemas.EmergencyContact,  tags=["Emergency Contact"])
def update_emergency_contact(
    *,
    db: Session = Depends(get_db),
    id: str,
    emergency_contact_in: schemas.EmergencyContactUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> EmergencyContact:
    emergency_contact_obj = emergency_contact.get(db=db, id=id)
    if not emergency_contact_obj:
        raise HTTPException(status_code=404, detail="emergency_contact not found")
    return emergency_contact.update(db=db, db_obj=emergency_contact_obj, obj_in=emergency_contact_in)

@api_router.delete("/emergency_contact/{id}", response_model=schemas.EmergencyContact,  tags=["Emergency Contact"])
def delete_emergency_contact(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> EmergencyContact:
    emergency_contact_obj = emergency_contact.get(db=db, id=id)
    if not emergency_contact_obj:
        raise HTTPException(status_code=404, detail="emergency_contact not found")
    return emergency_contact.remove(db=db, id=id)













#NextOfKin
@api_router.post("/next_of_kin/", response_model=schemas.NextOfKin, tags=["Next Of Kin"])
def create_next_of_kin(
    *,
    db: Session = Depends(get_db),
    next_of_kin_in: schemas.NextOfKinCreate,
    current_user: User = Depends(current_active_admin_user)
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

@api_router.get("/staff_next_of_kin/", response_model=List[schemas.NextOfKin],  tags=["Next Of Kin"])
def read_all_staff_next_of_kin(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(current_active_admin_user)
) -> List[NextOfKin]:
    next_of_kin_obj = next_of_kin.get_multi(db, skip=skip, limit=limit)
    return next_of_kin_obj

@api_router.get("/next_of_kin/{id}", response_model=schemas.NextOfKin,  tags=["Next Of Kin"])
def read_next_of_kin(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> NextOfKin:
    next_of_kin_obj = next_of_kin.get(db=db, id=id)
    if not next_of_kin_obj:
        raise HTTPException(status_code=404, detail="next_of_kin not found")
    return next_of_kin_obj

@api_router.put("/next_of_kin/{id}", response_model=schemas.NextOfKin,  tags=["Next Of Kin"])
def update_next_of_kin(
    *,
    db: Session = Depends(get_db),
    id: str,
    next_of_kin_in: schemas.NextOfKinUpdate,
    current_user: User = Depends(current_active_admin_user)
) -> NextOfKin:
    next_of_kin_obj = next_of_kin.get(db=db, id=id)
    if not next_of_kin_obj:
        raise HTTPException(status_code=404, detail="next_of_kin not found")
    return next_of_kin.update(db=db, db_obj=next_of_kin_obj, obj_in=next_of_kin_in)

@api_router.delete("/next_of_kin/{id}", response_model=schemas.NextOfKin,  tags=["Next Of Kin"])
def delete_next_of_kin(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(current_active_admin_user)
) -> NextOfKin:
    next_of_kin_obj = next_of_kin.get(db=db, id=id)
    if not next_of_kin_obj:
        raise HTTPException(status_code=404, detail="next_of_kin not found")
    return next_of_kin.remove(db=db, id=id)











from tempfile import NamedTemporaryFile, TemporaryDirectory
import logging

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

    
    # Create temporary file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        file_path = tmp_file.name
        #file_path = f"/uploads/images/bio_data_{bio_data_id}.pdf"
    try:
        path = generate_pdf_for_bio_data(bio_data, trademark, declarations, academics, professionals,history_of_employment ,emergency_contacts, next_of_kins, file_path)
        print("path: ", path)
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


