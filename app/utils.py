# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# from PIL import Image
# from io import BytesIO
# from fpdf import FPDF
#from database.db_session import get_db
from sqlalchemy.orm import Session
from models import BioData
from fastapi import HTTPException, status, UploadFile
#from sqlalchemy import inspect
import html
from typing import Union, Any
import re
import os
import json
from models import *  # Import your models here


# List of all models
all_models = [
    Centre, Directorate, Grade, EmploymentType, StaffCategory, BioData, EmploymentDetail, 
    BankDetail, Academic, Professional, Qualification, EmploymentHistory, FamilyInfo, EmergencyContact, NextOfKin, 
    Declaration, User
]




import os
import re
import html
import json
from typing import Union, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
#from sqlalchemy.sql import text
from sqlalchemy import text
from fastapi import UploadFile
import io
from sqlalchemy.exc import SQLAlchemyError
import logging




def execute_sql_file(db: Session, file_: UploadFile):
    """
    Executes SQL commands from a file using the provided SQLAlchemy session.

    Parameters:
    - db: SQLAlchemy Session object.
    - file_: FastAPI UploadFile object.
    """
    # Validate file type
    if not validate_file_type(file_.filename, ['.sql']):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .sql files are allowed.")

    try:
        # Read SQL file content from UploadFile
        file_content = io.StringIO(file_.file.read().decode('utf-8'))
        sql_content = file_content.read()

        # Sanitize SQL commands
        sanitized_sql = sanitize_sql(sql_content)

        # Split SQL commands by semicolon, ensuring semicolons in strings or comments are not split
        sql_commands = sanitized_sql.split(';\n')  # Better splitting strategy

        # Remove empty commands
        sql_commands = [command.strip() for command in sql_commands if command.strip()]

        # Begin a new transaction explicitly
        with db.begin():
            # Execute each command within the transaction
            for command in sql_commands:
                if command:  # Ensure the command is not empty
                    db.execute(text(command))

        # Commit is automatic with db.begin() if no exceptions occur

    except SQLAlchemyError as e:
        # Rollback is automatic with db.begin() if an exception occurs
        raise HTTPException(status_code=400, detail=f"SQLAlchemy error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def validate_file_type(filename: str, allowed_extensions: list) -> bool:
    """Validates the file type based on its extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in allowed_extensions

def sanitize_sql(sql_commands: str) -> str:
    """Sanitizes SQL commands to prevent SQL injection."""
    # Remove SQL comments
    sql_commands = re.sub(r'(--[^\n]*\n)|(/\*.*?\*/)', '', sql_commands, flags=re.DOTALL)
    
    # Normalize whitespace
    sql_commands = re.sub(r'\s+', ' ', sql_commands).strip()

    # Block risky SQL keywords (you can expand this list as needed)
    risky_keywords = ['DROP', 'TRUNCATE']
    pattern = re.compile(r'\b(' + '|'.join(risky_keywords) + r')\b', re.IGNORECASE)
    if pattern.search(sql_commands):
        raise ValueError("SQL contains risky operations that are not allowed.")
    
    # Escaping potentially dangerous characters (like single quotes)
    sql_commands = sql_commands.replace("'", "''")

    return sql_commands

def sanitize_json_data(data: Union[dict, list]) -> Union[dict, list]:
    """Sanitizes JSON data to prevent XSS or injection attacks."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                # Escaping HTML entities to prevent XSS
                sanitized_value = html.escape(value)
                
                # Removing any remaining potentially dangerous characters
                data[key] = re.sub(r'[<>]', '', sanitized_value)
            elif isinstance(value, (dict, list)):
                data[key] = sanitize_json_data(value)
            elif not isinstance(value, (int, float, bool, type(None))):
                # Ensure no unexpected data types
                raise ValueError(f"Invalid data type detected: {type(value)}")
    elif isinstance(data, list):
        data = [sanitize_json_data(item) for item in data]
    
    return data

def seed_data_from_json(db: Session, json_file: UploadFile, model: Any) -> None:
    """Seeds data from a sanitized JSON file into the given model."""
    allowed_extensions = ['.json']
    if not validate_file_type(json_file.filename, allowed_extensions):
        raise ValueError("Invalid file type. Only .json files are allowed.")
    
    try:
        data = json.load(json_file.file)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
    finally:
        json_file.file.close()  # Ensure file is closed after reading

    # Sanitize the JSON data to prevent XSS or injection attacks
    sanitized_data = sanitize_json_data(data)
    
    try:
        for item in sanitized_data:
            db_obj = model(**item)
            db.add(db_obj)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding data from JSON file: {str(e)}")


# def generate_pdf_for_bio_data(bio_data_id: str, db: Session):
#     # Fetch all related data for the given bio_data_id
#     bio_data = db.query(BioData).filter(BioData.id == bio_data_id).first()
#     if not bio_data:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BioData not found")

#     related_tables = [
#         (bio_data.employment_detail, "EmploymentDetail"),
#         (bio_data.bank_details, "BankDetail"),
#         (bio_data.academics, "Academic"),
#         (bio_data.professionals, "Professional"),
#         (bio_data.qualifications, "Qualification"),
#         (bio_data.employment_histories, "EmploymentHistory"),
#         (bio_data.family_infos, "FamilyInfo"),
#         (bio_data.emergency_contacts, "EmergencyContact"),
#         (bio_data.next_of_kins, "NextOfKin"),
#         (bio_data.declarations, "Declaration"),
#     ]

#     file_path = f"/tmp/bio_data_{bio_data_id}.pdf"
#     pdf = canvas.Canvas(file_path, pagesize=letter)
#     pdf.setTitle("Bio Data Report")

#     y_position = 10.5 * inch

#     pdf.drawString(1 * inch, y_position, f"BioData Report for ID: {bio_data_id}")
#     y_position -= 0.5 * inch

#     def get_column_names(model):
#         mapper = inspect(model.__class__)
#         return [prop.key for prop in mapper.attrs if prop.key not in ['id', f'{model.__tablename__}_id']]

#     for related_obj, table_name in related_tables:
#         if related_obj:
#             if isinstance(related_obj, list):
#                 for obj in related_obj:
#                     pdf.drawString(1 * inch, y_position, f"Table: {table_name}")
#                     y_position -= 0.2 * inch
#                     column_names = get_column_names(obj)
#                     for column in column_names:
#                         pdf.drawString(1.2 * inch, y_position, f"{column}: {getattr(obj, column)}")
#                         y_position -= 0.2 * inch
#             else:
#                 pdf.drawString(1 * inch, y_position, f"Table: {table_name}")
#                 y_position -= 0.2 * inch
#                 column_names = get_column_names(related_obj)
#                 for column in column_names:
#                     pdf.drawString(1.2 * inch, y_position, f"{column}: {getattr(related_obj, column)}")
#                     y_position -= 0.2 * inch

#     pdf.showPage()
#     pdf.save()

#     return file_path
