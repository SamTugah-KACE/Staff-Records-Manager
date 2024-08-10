from utils import sanitize_json_data, sanitize_sql, execute_sql_file, seed_data_from_json
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database.db_session import get_db
from models import *  # Import your models here
from typing import Any
from auth import current_active_admin

# List of all models
all_models = [
    Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, 
    BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]
router = APIRouter(prefix="/api/sys/")
#api_router = APIRouter(prefix="/api/sys/")

@router.post("/execute-sql/",tags=["System Admin Console"])
def execute_sql(db: Session = Depends(get_db), file_path: str = None, current_user: User = Depends(current_active_admin)):
    """Endpoint to execute SQL commands from a sanitized file."""
    try:
        execute_sql_file(db, file_path)
        return {"detail": "SQL commands executed successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/seed-data/",tags=["System Admin Console"])
def seed_data(db: Session = Depends(get_db), file_path: str = None, MyModel: Any = None, current_user: User = Depends(current_active_admin)):
    """Endpoint to seed sanitized data from a JSON file."""
    try:
        seed_data_from_json(db, file_path, MyModel)  # Replace MyModel with your model
        return {"detail": "Data seeded successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")