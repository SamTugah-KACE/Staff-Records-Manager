from utils import sanitize_json_data, sanitize_sql, execute_sql_file, seed_data_from_json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database.db_session import get_db
from models import *  # Import your models here
from typing import Any
from auth import current_active_sys_admin
import os

# List of all models
all_models = [
    Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, 
    BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]
router = APIRouter(prefix="/api")
#api_router = APIRouter(prefix="/api/sys/")



# Directory to store uploaded SQL files
UPLOAD_DIR = "uploads/db_files"

# Ensure the upload directory exists
#os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/execute-sql/", tags=["System Admin Console"])
async def execute_sql(db: Session = Depends(get_db), file_: UploadFile = File(...), current_user: User = Depends(current_active_sys_admin)):
    """Endpoint to execute SQL commands from a sanitized file."""

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    file_location = os.path.join(UPLOAD_DIR, file_.filename)
    
    try:
        # Save the uploaded file to the upload directory
        with open(file_location, "wb") as buffer:
            buffer.write(await file_.read())
        try:
            await execute_sql_file(file_location)
        except HTTPException as e:
        # Return error details if SQL execution fails
            raise e
    
        return {"status": "success", "detail": "SQL file executed successfully"}
    

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Unexpected error occured: {str(ex)}")
    


@router.post("/seed-data/", tags=["System Admin Console"])
def seed_data(db: Session = Depends(get_db), file_: UploadFile = File(...), model: Any = None, current_user: User = Depends(current_active_sys_admin)):
    """Endpoint to seed sanitized data from a JSON file."""
    try:
        seed_data_from_json(db, file_, model)  # Replace model with your specific model
        return {"detail": "Data seeded successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")