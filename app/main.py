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
from oauth_api import auth_router
from sqladmin import Admin, ModelView
from dashboard import *



def create_tables():
    Base.metadata.create_all(bind=engine)
    # Base.metadata.drop_all(bind=engine)



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





def start_application():
    app = FastAPI(docs_url="/api", title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.add_middleware(
    CORSMiddleware,
    allow_origins= ['https://staff-records-management-system-f6y8.onrender.com',  'https://staff-records-management-system.onrender.com' ],
    allow_credentials=True,    
    allow_methods=["*"],
    allow_headers=["*"]
    )
    create_tables()
    include_router(app)
    #lifespan(app)

    return app

app = start_application()


admin = Admin(app, engine, title="System Console")
admin.add_view(Trademark)
admin.add_view(Center)
admin.add_view(Directorate)
admin.add_view(Grade)
admin.add_view(EmploymentType)
admin.add_view(StaffCategory)
admin.add_view(Staff)
admin.add_view(UserAdmin)
admin.add_view(Academic)
admin.add_view(Professional)
admin.add_view(Qualification)
admin.add_view(BankDetail)
admin.add_view(EmploymentDetail)
admin.add_view(FamilyInfo)
admin.add_view(EmergencyContact)
admin.add_view(NextOfKin)
admin.add_view(EmploymentHistory)
admin.add_view(Declaration)




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



from fastapi import Request, HTTPException, Depends
import requests
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from database.db_session import get_db
import os

#intruder_list = []


# class IntruderDetectionMiddleware:
#     async def __call__(self, request: Request, call_next):
#         client_ip = request.client.host
#         if client_ip in [intruder['ip_address'] for intruder in intruder_list]:
#             raise HTTPException(status_code=403, detail="Access Denied: You are not authorized to access this server.")

#         response = await call_next(request)
#         if response.status_code == 401 or response.status_code == 403:
#             await log_intruder_info(request)

#         return response

class IntruderDetectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db: Session = Depends(get_db)):
        super().__init__(app)
        self.db = db
    
    async def intruder_info(request: Request):
        #intruder_list = []
        client_ip = request.client.host
        headers = request.headers
        user_agent = headers.get("User-Agent")
        mac_address = headers.get("X-MAC-Address")  # Custom header for MAC Address
        location = requests.get(f"https://ipinfo.io/{client_ip}/geo").json()

        intruder_info = {
            "ip_address": client_ip,
            "mac_address": mac_address,
            "user_agent": user_agent,
            "location": location,
        }
        print("intruder info dict: ", intruder_info)
        settings.intruder_list.append(intruder_info)
        print(f"Intruder detected: {intruder_info}")

        return intruder_info


    async def log_intruder_info(ip_addr: str, mac_addr: str, user_agent: str, location: str):
        # Get current date to create or append to the log file
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file_name = f"intruder_log_{current_date}.txt"
        log_directory = "security/logs/"

        os.makedirs(log_directory, exist_ok=True)
        

        # Check if the log file exists
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        
        log_filepath = os.path.join(log_directory, log_file_name)
        

        # Create log entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{ip_addr} | {mac_addr} | {user_agent} | {location} | {timestamp}"

        # Check if the log file already exists
        if os.path.exists(log_filepath):
            with open(log_filepath, 'a') as file:
                file.write("================================================================================\n")
                file.write(log_entry + "\n")
        else:
            with open(log_file_name, 'w') as file:
                file.write("IP Addr | Mac Addr | User Agent | location | Timestamp\n")
                file.write(log_entry + "\n")

        return log_filepath

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        print("response in middleware: ", response)
        # Example of handling rate limit exceeded and locking accounts
        if response.status_code == 429:  # Too Many Requests
            username = request.headers.get("X-Username")
            print("\nusername in middleware: ", username)
            if username:
                user = self.db.query(User).filter(User.username == username).first()
                if user:
                    print("user in middleware: ", user)
                    user.lock_account(lock_time_minutes=10)
                    self.db.commit()
                    info = await IntruderDetectionMiddleware.intruder_info(request=request)
                    log = await IntruderDetectionMiddleware.log_intruder_info(info.get('ip_address'), info.get('mac_address'), info.get('user_agent'), info.get('location'))

                    print("log info: ", log)


        return response

#app.middleware("http")(IntruderDetectionMiddleware())
app.add_middleware(IntruderDetectionMiddleware)



if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, log_level="info", reload = True)
    print("running")