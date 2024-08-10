from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy import inspect
from typing import Any, Type, Generic, TypeVar, Optional, List
from pydantic import BaseModel
#from schemas import NextOfKinCreate
from models import (NextOfKin, EmergencyContact, 
                    EmploymentDetail, EmploymentType, 
                    StaffCategory, Grade, Centre, Directorate, BankDetail,
                    Academic, Professional, Qualification,
                    EmploymentHistory, EmergencyContact, FamilyInfo)  
import schemas



ModelType = TypeVar('ModelType', bound=BaseModel)
#ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: str) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ModelType]:
        obj = db.query(self.model).filter(getattr(self.model, field) == value).first()
       
        return obj
    def create(self, db: Session, obj_in: ModelType) -> ModelType:
        try:
            self.check_unique_fields(db, obj_in)
            db_obj = self.model(**obj_in.dict())
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise ValueError("Data already exists with conflicting unique fields") from e

    def update(self, db: Session, db_obj: ModelType, obj_in: ModelType) -> ModelType:
        try:
            self.check_unique_fields(db, obj_in, exclude_id=db_obj.id)
            for field in obj_in.dict(exclude_unset=True):
                setattr(db_obj, field, getattr(obj_in, field))
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise ValueError("Data update would conflict with existing unique fields") from e

    def remove(self, db: Session, id: str) -> ModelType:
        db_obj = db.query(self.model).get(id)
        if not db_obj:
            raise ValueError("Data not found")

        try:
            self.check_integrity_constraints(db, db_obj)
            db.delete(db_obj)
            db.commit()
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="Deleting this data violates integrity constraints") from e

    def check_unique_fields(self, db: Session, obj: ModelType, exclude_id: Optional[str] = None):
        unique_fields = self.model.__table__.indexes
        for field in unique_fields:
            if field.unique:
                query = db.query(self.model).filter(getattr(self.model, field.columns[0].name) == getattr(obj, field.columns[0].name))
                if exclude_id:
                    query = query.filter(self.model.id != exclude_id)
                existing_obj = query.first()
                if existing_obj:
                    raise IntegrityError("Conflicting unique field", obj, field.columns[0].name)

    def check_integrity_constraints(self, db: Session, obj: ModelType):
        mapper = inspect(self.model)
        for relationship in mapper.relationships:
            related_class = relationship.mapper.class_
            related_attr = getattr(self.model, relationship.key)
            if isinstance(related_attr.property, RelationshipProperty):
                related_objs = getattr(obj, relationship.key)
                if related_objs is not None:
                    if isinstance(related_objs, list):
                        for related_obj in related_objs:
                            if not self._check_relationship_integrity(db, related_obj):
                                raise IntegrityError(f"Deleting this data violates integrity constraints with {related_class.__name__}")
                                #raise IntegrityError(f"Deleting this data violates integrity constraints with other related table(s)")
                                
                    else:
                        if not self._check_relationship_integrity(db, related_objs):
                            raise IntegrityError(f"Deleting this data violates integrity constraints with {related_class.__name__}")
                            #raise IntegrityError(f"Deleting this data violates integrity constraints with other related table(s)")

    def _check_relationship_integrity(self, db: Session, related_obj):
        related_class = type(related_obj)
        related_primary_keys = inspect(related_class).primary_key
        query = db.query(related_class)
        for pk in related_primary_keys:
            query = query.filter(pk == getattr(related_obj, pk.name))
        return query.first() is None



class CRUDCentre(CRUDBase[schemas.Centre, schemas.CentreCreate, schemas.CentreUpdate]):
    pass

centre = CRUDCentre(Centre)


#directorate
class CRUDDirectorate(CRUDBase[schemas.Directorate, schemas.DirectorateCreate, schemas.DirectorateUpdate]):
    pass

directorate = CRUDDirectorate(Directorate)


#Grade
class CRUDGrade(CRUDBase[schemas.Grade, schemas.GradeCreate, schemas.GradeUpdate]):
    pass

grade = CRUDGrade(Grade)


#employment type
class CRUDEmploymentType(CRUDBase[schemas.EmploymentType, schemas.EmploymentTypeCreate, schemas.EmploymentTypeUpdate]):
    pass

employment_type = CRUDEmploymentType(EmploymentType)


#staffcategory
class CRUDStaffCategory(CRUDBase[schemas.StaffCategory, schemas.StaffCategoryCreate, schemas.StaffCategoryUpdate]):
    pass

staff_category = CRUDStaffCategory(StaffCategory)


#employment details
class CRUDEmploymentDetail(CRUDBase[schemas.EmploymentDetail, schemas.EmploymentDetailCreate, schemas.EmploymentDetailUpdate]):
    pass

employment_detail = CRUDEmploymentDetail(EmploymentDetail)


#BankDetail
class CRUDBankDetail(CRUDBase[schemas.BankDetail, schemas.BankDetailCreate, schemas.BankDetailUpdate]):
    pass

bank_detail = CRUDBankDetail(BankDetail)


#academic
class CRUDAcademic(CRUDBase[schemas.Academic, schemas.AcademicCreate, schemas.AcademicUpdate]):
    pass

academic = CRUDAcademic(Academic)


#professional
class CRUDProfessional(CRUDBase[schemas.Professional, schemas.ProfessionalCreate, schemas.ProfessionalUpdate]):
    pass

professional = CRUDProfessional(Professional)



#Qualification
class CRUDQualification(CRUDBase[schemas.Qualification, schemas.QualificationCreate, schemas.CentreUpdate]):
    pass

qualification = CRUDQualification(Qualification)



#employment history
class CRUDEmploymentHistory(CRUDBase[schemas.EmploymentHistory, schemas.EmploymentHistoryCreate, schemas.EmploymentHistoryUpdate]):
    pass

employment_history = CRUDEmploymentHistory(EmploymentHistory)


#EmergencyContact
class CRUDEmergencyContact(CRUDBase[schemas.EmergencyContact, schemas.EmergencyContactCreate, schemas.EmergencyContactUpdate]):
    pass

emergency_contact = CRUDEmergencyContact(EmergencyContact)



#NextOfKin
class CRUDNextOfKin(CRUDBase[schemas.NextOfKin, schemas.NextOfKinCreate, schemas.NextOfKinUpdate]):
    pass
    #  def create(self, db: Session, obj_in: NextOfKinCreate) -> NextOfKin:
    #     # Check if a NextOfKin with the same phone number already exists
    #     existing = db.query(self.model).filter_by(phone=obj_in.phone).first()
    #     if existing:
    #         raise ValueError("Next of Kin with this phone number already exists")

    #     return super().create(db, obj_in=obj_in)

next_of_kin = CRUDNextOfKin(NextOfKin)


#familyinfo
class CRUDFamilyInfo(CRUDBase[schemas.FamilyInfo, schemas.FamilyInfoCreate, schemas.FamilyInfoUpdate]):
    pass

family_info = CRUDFamilyInfo(FamilyInfo)