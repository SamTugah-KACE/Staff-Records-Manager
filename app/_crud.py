from sqlalchemy.orm import Session, joinedload, contains_eager, aliased
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
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
                    EmploymentHistory, EmergencyContact, FamilyInfo, UserRole, BioData)  
import schemas
from sqlalchemy.exc import SQLAlchemyError
import uuid
from uuid import UUID









# Custom Exception for Integrity Constraint Violations
class IntegrityConstraintViolation(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


ModelType = TypeVar('ModelType', bound=BaseModel)
#ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

def get_model_id_by_related_id(
    db: Session,
    model: Type,  # SQLAlchemy model, not Pydantic BaseModel
    related_id: UUID
) -> Optional[UUID]:
    """
    Retrieve the primary ID of a given model using a related row's foreign key ID.

    :param db: SQLAlchemy session to use for querying
    :param model: The SQLAlchemy model class whose ID we are looking for
    :param related_id: The UUID of the related row
    :return: The primary UUID of the model, or None if not found
    """
    try:
        # Loop through relationships in the model to find foreign key relationships
        for relationship in model.__mapper__.relationships:
            related_model = relationship.mapper.class_

            # Check if the related model's primary key matches the provided `related_id`
            related_row = db.query(related_model).filter(related_model.id == related_id).first()

            if related_row:
                # Load the relationship using the class-bound attribute (not strings)
                model_row = db.query(model).options(joinedload(getattr(model, relationship.key)))\
                    .filter(getattr(model, relationship.key) == (related_row))\
                    .first()

                if model_row:
                    return model_row.id

        raise HTTPException(status_code=404, detail="No matching record found with the given related ID")

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
# def get_model_id_by_related_id(
#         db: Session,
#         model: Type[BaseModel],
#         related_id: UUID
#         ) -> Optional[UUID]:
#         """
#         Retrieve the primary ID of a given model using a related row's foreign key ID.

#         :param db: SQLAlchemy session to use for querying
#         :param model: The model class whose ID we are looking for
#         :param related_id: The UUID of the related row
#         :return: The primary UUID of the model, or None if not found
#         """
#         try:
#             # Loop through relationships in the model to find foreign key relationships
#             for relationship in model.__mapper__.relationships:
#                 # Retrieve the related model class
#                 related_model = relationship.mapper.class_

#                 print("\nrelated_model: ", related_model)

#                 # Check if the related model's primary key matches the provided `related_id`
#                 related_row = db.query(related_model).filter(related_model.id == related_id).first()
#                 print("\nrelated row: ", related_row)
#                 if related_row:
#                     # Fetch the row from the main model using the related model's foreign key
#                     model_row = db.query(model).options(joinedload(relationship.key))\
#                         .filter(getattr(model, relationship.key).contains(related_row))\
#                         .first()
#                     print("\nmodel row: ", model_row)
#                     if model_row:
#                         print("\nmodel_row.id: ", model_row.id)
#                         return model_row.id

#             raise HTTPException(status_code=404, detail="No matching record found with the given related ID")

#         except SQLAlchemyError as e:
#             db.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}")
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    
        

    def get(self, db: Session, id: str) -> Optional[ModelType]:
        idn = db.query(self.model).filter(self.model.id == id).first()
        print("\nobj: ", idn)
        if not idn:
            print("bio_row_id****")
            idn = db.query(self.model).filter(self.model.bio_row_id == id).first()
            print("\nresulting obj ^: ", idn)
        
        return idn
    

    def get_(self, db: Session, id: str, bio_row_id: Optional[str] = None) -> Optional[ModelType]:
        query = db.query(self.model)
        if bio_row_id:
            return query.filter(self.model.bio_row_id == bio_row_id).first()
        return query.filter(self.model.id == id).first()

    
    def get_detailed_(self, db:Session, model, id) -> Optional[ModelType]:
        try:
            # Start with the base query
            query = db.query(model)
            
            # Loop through relationships and use class-bound attributes directly
            for relationship in model.__mapper__.relationships:
                # Get the class-bound attribute
                relationship_attr = getattr(model, relationship.key)
                query = query.options(joinedload(relationship_attr))

            # Fetch the record by ID
            return query.filter(model.id == id).first()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    

    def get_detailed(self, db: Session, model: Type[ModelType], id: uuid.UUID) -> Optional[ModelType]:
        try:
            # Start with the base query for the primary model
            query = db.query(model)

            # Loop through relationships and load related data
            for relationship in model.__mapper__.relationships:
                relationship_attr = getattr(model, relationship.key)
                query = query.options(joinedload(relationship_attr))

            # Check if the provided UUID matches the model's primary key
            result = query.filter(model.id == id).first()

            # If no result by primary key, check for a match in related rows by foreign key
            if not result:
                for relationship in model.__mapper__.relationships:
                    related_model = relationship.mapper.class_
                    foreign_key_column = relationship.local_remote_pairs[0][0]
                    
                    # Join the related model and filter by related model's UUID foreign key
                    related_query = db.query(model).join(related_model).filter(foreign_key_column == id).first()
                    
                    if related_query:
                        return related_query

            return result

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")



    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    # def get_multi_field(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
    #     return db.query(self.model.roles).offset(skip).limit(limit).all()
    
    # def get_multi_with_join(self, db: Session, skip: int = 0, limit: int = 10) -> List[ModelType]:
    #     query = db.query(self.model)
    #     # Auto join related tables using joinedload
    #     for rel in inspect(self.model).relationships:
    #         query = query.options(joinedload(rel.key))
    #     return query.offset(skip).limit(limit).all()
    

    def get_multi_with_model(self, db: Session, model: Type[ModelType], skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            # Start with the base query
            query = db.query(model)
            
            # Loop through relationships and use class-bound attributes directly
            for relationship in model.__mapper__.relationships:
                # Get the class-bound attribute
                relationship_attr = getattr(model, relationship.key)
                query = query.options(joinedload(relationship_attr))

            # Fetch multiple records
            return query.offset(skip).limit(limit).all()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
        


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

    # def update(self, db: Session, db_obj: ModelType, obj_in: ModelType) -> ModelType:
    #     try:
    #         self.check_unique_fields(db, obj_in, exclude_id=db_obj.id)
    #         for field in obj_in.dict(exclude_unset=True):
    #             setattr(db_obj, field, getattr(obj_in, field))
    #         db.add(db_obj)
    #         db.commit()
    #         db.refresh(db_obj)
    #         return db_obj
    #     except IntegrityError as e:
    #         db.rollback()
    #         raise ValueError("Data update would conflict with existing unique fields") from e

    # def remove(self, db: Session, id: str, force_delete: bool = False) -> ModelType:
    #     db_obj = db.query(self.model).get(id)
    #     if not db_obj:
    #         raise HTTPException(status_code=404, detail="Data not found")

    #     try:
    #         if not force_delete:
    #             # Perform the integrity check only if force_delete is False
    #             self.check_integrity_constraints(db, db_obj)

    #         db.delete(db_obj)
    #         db.commit()
    #         return db_obj
    #     except IntegrityConstraintViolation as e:
    #         db.rollback()
    #         raise HTTPException(status_code=400, detail=str(e))
        # except IntegrityError as e:
        #     db.rollback()
        #     raise HTTPException(status_code=400, detail="Deleting this data violates integrity constraints") from e



    def update(self, db: Session, db_obj: ModelType, obj_in: ModelType) -> ModelType:
        try:
            # Check for uniqueness based on provided data, excluding the object's own ID
            self.check_unique_fields(db, obj_in, exclude_id=db_obj.id)
            
            # Attempt to set new values from the input object
            for field in obj_in.dict(exclude_unset=True):
                print("field in update fields: ", field)
                setattr(db_obj, field, getattr(obj_in, field))
            
            print("\nupdate db_obj: ", db_obj)
            # Save the updated object
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        
        except IntegrityError as e:
            db.rollback()
            raise ValueError("Data update would conflict with existing unique fields") from e
        except Exception as e:
            print("500 error: ", e)
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


    def remove(self, db: Session, id: uuid.UUID, force_delete: bool = False) -> ModelType:
        try:
            # Try to retrieve the object by the primary key ID
            db_obj = db.query(self.model).filter(self.model.id == id).first()

            # If not found by primary key, check for matching related row by foreign key
            if not db_obj:
                for relationship in self.model.__mapper__.relationships:
                    related_model = relationship.mapper.class_
                    foreign_key_column = relationship.local_remote_pairs[0][0]
                    
                    # Query based on the foreign key in the related model
                    db_obj = db.query(self.model).join(related_model).filter(foreign_key_column == id).first()
                    
                    # Break if a related object is found
                    if db_obj:
                        break
            
            if not db_obj:
                raise HTTPException(status_code=404, detail="Data not found")

            # Handle soft or force delete
            if not force_delete:
                # Perform integrity checks if force_delete is False
                self.check_integrity_constraints(db, db_obj)

            db.delete(db_obj)
            db.commit()
            return db_obj
        
        except IntegrityConstraintViolation as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")




    def check_unique_fields(self, db: Session, obj: ModelType, exclude_id: Optional[uuid.UUID] = None):
        # Retrieve unique columns from the model's table
        unique_columns = [col for col in self.model.__table__.columns if col.unique]
        
        for column in unique_columns:
            # Build the query to check for conflicts on unique fields
            query = db.query(self.model).filter(getattr(self.model, column.name) == getattr(obj, column.name))
            
            # Exclude the current object from the uniqueness check by its ID
            if exclude_id:
                query = query.filter(self.model.id != exclude_id)

            # Fetch the first record that would cause a conflict
            existing_obj = query.first()

            if existing_obj:
                raise IntegrityConstraintViolation(f"Conflict found with unique field: '{column.name}'")

        # Check for uniqueness in related models' foreign key fields, if any
        for relationship in self.model.__mapper__.relationships:
            related_model = relationship.mapper.class_
            
            # Get the related column (foreign key)
            foreign_key_column = relationship.local_remote_pairs[0][0]
            
            # Check for related rows that have conflicting unique fields
            for related_column in related_model.__table__.columns:
                if related_column.unique:
                    related_query = db.query(related_model).filter(
                        getattr(related_model, related_column.name) == getattr(obj, related_column.name)
                    )

                    # Exclude the current object's related row from the check
                    if exclude_id:
                        related_query = related_query.filter(foreign_key_column != exclude_id)
                    
                    existing_related_obj = related_query.first()

                    if existing_related_obj:
                        raise IntegrityConstraintViolation(f"Conflict found in related unique field: '{related_column.name}'")

    # def check_unique_fields(self, db: Session, obj: ModelType, exclude_id: Optional[str] = None):
    #     # Iterate over all columns to find unique ones
    #     unique_columns = [col for col in self.model.__table__.columns if col.unique]
        
    #     for column in unique_columns:
    #         # Build the query for each unique field
    #         query = db.query(self.model).filter(getattr(self.model, column.name) == getattr(obj, column.name))
            
    #         # Exclude the current object by ID if exclude_id is provided
    #         if exclude_id:
    #             query = query.filter(self.model.id != exclude_id)
            
    #         # Check for existing records that would cause a conflict
    #         existing_obj = query.first()
    #         if existing_obj:
    #             raise IntegrityConstraintViolation(f"Conflict found with unique field: '{column.name}'")
                        #raise IntegrityError("Conflicting unique field", obj, field.columns[0].name)

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
                                 raise IntegrityConstraintViolation(
                                f"Deleting this data violates integrity constraints with {related_class.__name__}"
                            )
                                #raise IntegrityError(f"Deleting this data violates integrity constraints with {related_class.__name__}")
                                #raise IntegrityError(f"Deleting this data violates integrity constraints with other related table(s)")
                                
                    else:
                        if not self._check_relationship_integrity(db, related_objs):
                             raise IntegrityConstraintViolation(
                                f"Deleting this data violates integrity constraints with {related_class.__name__}"
                            )
                            #raise IntegrityError(f"Deleting this data violates integrity constraints with {related_class.__name__}")
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


class CRUDRole(CRUDBase[schemas.Role, schemas.RoleCreate, schemas.RoleUpdate]):
    pass

role = CRUDRole(UserRole)