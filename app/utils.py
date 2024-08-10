# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# from PIL import Image
# from io import BytesIO
# from fpdf import FPDF
#from database.db_session import get_db
from sqlalchemy.orm import Session
from models import BioData
from fastapi import HTTPException, status
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




def sanitize_json_data(data: Union[dict, list]) -> Union[dict, list]:
    """
    Sanitizes JSON data to prevent XSS or injection attacks.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = re.sub(r'[<>]', '', value)  # Removing characters that could be used in XSS
            elif isinstance(value, (dict, list)):
                data[key] = sanitize_json_data(value)
    elif isinstance(data, list):
        data = [sanitize_json_data(item) for item in data]
    
    return data


def execute_sql_file(db: Session, file_: Any) -> None:
    """Executes a given SQL file securely."""
    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=404, detail="SQL file not found.")
    
    allowed_extensions = ['.sql']
    if not validate_file_type(file_, allowed_extensions):
        raise ValueError("Invalid file type. Only .sql files is allowed.")


    with open(file_, 'r') as file:
        sql_commands = file.read()
        
        # Sanitize the SQL commands to prevent SQL injection
        sanitized_sql_commands = sanitize_sql(sql_commands)
        
        try:
            db.execute(sanitized_sql_commands)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error executing SQL file: {str(e)}")
        

def validate_file_type(file_: Any, allowed_extensions: list) -> bool:
    """
    Validates the file type based on its extension.
    """
    file_path = file_.filename
    _, ext = os.path.splitext(file_path)
    return ext.lower() in allowed_extensions

# Example usage
allowed_extensions = ['.sql', '.json']
file_path = '/path/to/uploaded/file.sql'

if not validate_file_type(file_path, allowed_extensions):
    raise ValueError("Invalid file type. Only .sql and .json files are allowed.")




def sanitize_sql(sql_commands: str) -> str:
    """
    Sanitizes SQL commands to prevent SQL injection.
    - Removes comments and unnecessary whitespaces.
    - Blocks risky SQL keywords.
    - Escapes potentially dangerous characters.
    """
    # Remove SQL comments
    sql_commands = re.sub(r'(--[^\n]*\n)|(/\*.*?\*/)', '', sql_commands, flags=re.DOTALL)
    
    # Normalize whitespace
    sql_commands = re.sub(r'\s+', ' ', sql_commands).strip()

    # Block risky SQL keywords (you can expand this list as needed)
    risky_keywords = ['DROP', 'TRUNCATE', 'ALTER', 'DELETE', 'INSERT', 'UPDATE']
    pattern = re.compile(r'\b(' + '|'.join(risky_keywords) + r')\b', re.IGNORECASE)
    if pattern.search(sql_commands):
        raise ValueError("SQL contains risky operations that are not allowed.")
    
    # Escaping potentially dangerous characters (like single quotes)
    sql_commands = sql_commands.replace("'", "''")

    return sql_commands



def sanitize_json_data(data: Union[dict, list]) -> Union[dict, list]:
    """
    Sanitizes JSON data to prevent XSS or injection attacks.
    - Removes potentially dangerous characters and HTML tags.
    - Escapes HTML entities to prevent XSS.
    - Ensures data types are valid.
    """

    allowed_extensions = ['.json']
    if not validate_file_type(file_path, allowed_extensions):
        raise ValueError("Invalid file type. Only .json files is allowed.")

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

def seed_data_from_json(db: Session, json_file_path: str, model: Any) -> None:
    """Seeds data from a sanitized JSON file into the given model."""
    # if not os.path.exists(json_file_path):
    #     raise HTTPException(status_code=404, detail="JSON file not found.")
    
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        
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
