from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from database.db_session import get_db
from sqlalchemy.orm import Session
from models import BioData
from fastapi import FastAPI, HTTPException, status
from sqlalchemy import inspect



def generate_pdf_for_bio_data(bio_data_id: str, db: Session):
    # Fetch all related data for the given bio_data_id
    bio_data = db.query(BioData).filter(BioData.id == bio_data_id).first()
    if not bio_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BioData not found")

    related_tables = [
        (bio_data.employment_detail, "EmploymentDetail"),
        (bio_data.bank_details, "BankDetail"),
        (bio_data.academics, "Academic"),
        (bio_data.professionals, "Professional"),
        (bio_data.qualifications, "Qualification"),
        (bio_data.employment_histories, "EmploymentHistory"),
        (bio_data.family_infos, "FamilyInfo"),
        (bio_data.emergency_contacts, "EmergencyContact"),
        (bio_data.next_of_kins, "NextOfKin"),
        (bio_data.declarations, "Declaration"),
    ]

    file_path = f"/tmp/bio_data_{bio_data_id}.pdf"
    pdf = canvas.Canvas(file_path, pagesize=letter)
    pdf.setTitle("Bio Data Report")

    y_position = 10.5 * inch

    pdf.drawString(1 * inch, y_position, f"BioData Report for ID: {bio_data_id}")
    y_position -= 0.5 * inch

    def get_column_names(model):
        mapper = inspect(model.__class__)
        return [prop.key for prop in mapper.attrs if prop.key not in ['id', f'{model.__tablename__}_id']]

    for related_obj, table_name in related_tables:
        if related_obj:
            if isinstance(related_obj, list):
                for obj in related_obj:
                    pdf.drawString(1 * inch, y_position, f"Table: {table_name}")
                    y_position -= 0.2 * inch
                    column_names = get_column_names(obj)
                    for column in column_names:
                        pdf.drawString(1.2 * inch, y_position, f"{column}: {getattr(obj, column)}")
                        y_position -= 0.2 * inch
            else:
                pdf.drawString(1 * inch, y_position, f"Table: {table_name}")
                y_position -= 0.2 * inch
                column_names = get_column_names(related_obj)
                for column in column_names:
                    pdf.drawString(1.2 * inch, y_position, f"{column}: {getattr(related_obj, column)}")
                    y_position -= 0.2 * inch

    pdf.showPage()
    pdf.save()

    return file_path
