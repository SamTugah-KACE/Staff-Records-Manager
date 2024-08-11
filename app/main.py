from fastapi.middleware.cors import CORSMiddleware
#from utils.database import engine,SessionLocal
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI,Request,status
import uvicorn
from apis import api_router
from Config.config import settings
from contextlib import asynccontextmanager
from database.setup import check_and_create_database
from fastapi.responses import JSONResponse
from database.db_session import engine
from database.admin import router
from models import Base, User, BioData
from auth import auth_router
from sqladmin import Admin, ModelView




def create_tables():
    Base.metadata.create_all(bind=engine)



## adding our api routes 
def include_router(app):
    app.include_router(auth_router)
    app.include_router(api_router)
    app.include_router(router)
    
    


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("processing...")
        await check_and_create_database()
        yield
    finally:
        print("Startup completed!") 

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.bio_row_id, User.email, User.username, User.hashed_password, User.role]

class Staff(ModelView, model=BioData):
    column_list = [BioData.id, BioData.title, BioData.first_name, BioData.surname, BioData, BioData.email]



def start_application():
    app = FastAPI(docs_url="/", title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,    
    allow_methods=["*"],
    allow_headers=["*"]
    )
    #create_tables()
    include_router(app)
    #lifespan(app)

    return app

app = start_application()


admin = Admin(app, engine, title="System Console")
admin.add_view(UserAdmin)
admin.add_view(Staff)


@app.on_event("startup")
async def startup_event():
    async with lifespan(app):
        pass



# Custom error handling middleware
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_message = "Validation error occurred"
    # Optionally, you can log the error or perform additional actions here
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error_message+f"{exc}"})

# Generic error handler for all other exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_message = "An unexpected error occurred:\n"
    # Optionally, you can log the error or perform additional actions here
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error_message+f"{exc}"})




if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, log_level="info", reload = True)
    print("running")