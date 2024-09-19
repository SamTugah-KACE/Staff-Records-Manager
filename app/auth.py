from datetime import datetime, timedelta, timezone
import fastapi.encoders
import flask
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, FastAPI
from sqlalchemy.orm import Session
import crud
from Config.config import settings
from database.db_session import get_db
import schemas
from schemas import TokenData
from fastapi_limiter.depends import RateLimiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
# from login_auth import login_service 
import models
from security import Security
from fastapi.encoders import jsonable_encoder
from fastapi import BackgroundTasks
import os
from fastapi.responses import FileResponse
import requests
from log_ import *
from fastapi.responses import PlainTextResponse



# app = FastAPI()

# auth_router = APIRouter(
#     #prefix="/api",
#     tags=["Authentication"],
#     responses={404: {"description": "Not found"}},
# )





# JWT configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password='password'):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print("username :", username)
        # if username is None:
        #     raise credentials_exception
        # token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    print("user obj: ", user)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.is_active != True:
        raise HTTPException(status_code=400, detail="User's account is Inactive.")
    return current_user

def getCurrentUserDashbaord(current_user: models.User, db:Session = Depends(get_db)):
    #role = None
    dash = None
    print("current user: ", current_user.role)
    try:
        
        # if current_user.is_active != True:
        #     raise HTTPException(status_code=400, detail="User's account is Inactive.")
        user = db.query(models.UserRole).filter(models.UserRole.roles == current_user.role).first()
        dash = user.dashboard
        print("Current User Role: ", user.roles)
        print("Current User Dashboard: ", user.dashboard)
        return dash
    
    except Exception as e:
        print("exception checking current user role Dashboard: ", e)
        raise HTTPException(status_code=400, detail=str(e))



def current_active_admin(current_user: schemas.User = Depends(get_current_active_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admins Only")
    return current_user

def current_active_sys_admin(current_user: schemas.User = Depends(get_current_active_user)):
    if current_user.role != "Sys. Admin":
        raise HTTPException(status_code=403, detail="Systems Admin Only")
    return current_user

def current_active_user(current_user: schemas.User = Depends(get_current_active_user)):
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Users Only")
    return current_user

# def current_active_admin_user(current_user: schemas.User = Depends(get_current_active_user)):
#     print("user.role: ", current_user.role)
#     if (current_user.role != "admin") and (current_user.role != "user"):
#         raise HTTPException(status_code=403, detail="Unknown User")
#     return current_user


def current_active_admin_user(current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Fetch the role from the UserRole table
    user_role = db.query(models.UserRole).filter(models.UserRole.roles == current_user.role).first()

    # If role is not found or is not authorized, raise an error
    if not user_role:
        raise HTTPException(status_code=403, detail="Access denied. Unauthorized user.")
    print("current user in depends = ", current_user)
    return current_user


def is_authorized_role(roles: list, current_user: schemas.User = Depends(get_current_active_user)):
    return any(role.lower() in current_user.role.lower() for role in roles)

def check_admin_registration_limit(db: Session, current_user: schemas.User = Depends(get_current_active_user)):
    if "admin" in current_user.role.lower():
        existing_registration = db.query(models.BioData).filter(models.BioData.registered_by == current_user.role).first()
        if existing_registration:
            raise HTTPException(status_code=400, detail="System Admin has already registered a user.")


# @auth_router.post("/token", response_model=schemas.Token)
# def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, 
#             "token_type": "bearer",
#             "user":{"id": user.id,
#                     "username": user.username,
#                     "role": user.role
#                     }
#                     }



# # Initialize the Limiter
# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
# #app.add_exception_handler(RateLimitExceeded, limiter._rate_limit_exceeded_handler)

# # Add SlowAPI middleware
# app.add_middleware(SlowAPIMiddleware)

# # Custom exception handler for rate limiting
# @app.exception_handler(RateLimitExceeded)
# async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
#     return Response(
#         content="Rate limit exceeded, please try again later.",
#         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#     )



# async def intruder_info(request: Request):
#         #intruder_list = []
#         client_ip = request.client.host
#         headers = request.headers
#         user_agent = headers.get("User-Agent")
#         mac_address = headers.get("X-MAC-Address")  # Custom header for MAC Address
#         location = requests.get(f"https://ipinfo.io/{client_ip}/geo").json()

#         intruder_info = {
#             "ip_address": client_ip,
#             "mac_address": mac_address,
#             "user_agent": user_agent,
#             "location": location,
#         }
#         print("intruder info dict: ", intruder_info)
#         settings.intruder_list.append(intruder_info)
#         print(f"Intruder detected: {intruder_info}")

#         return intruder_info


# async def log_intruder_info(ip_addr: str, mac_addr: str, user_agent: str, location: str):
#     # Get current date to create or append to the log file
#     current_date = datetime.now().strftime('%Y-%m-%d')
#     log_file_name = f"intruder_log_{current_date}.txt"
#     log_directory = "security/logs/"

#     os.makedirs(log_directory, exist_ok=True)
    
#     print("log directory: ", log_directory)
#     # Check if the log file exists
#     if not os.path.exists(log_directory):
#         os.makedirs(log_directory)

    
#     log_filepath = os.path.join(log_directory, log_file_name)
    

#     # Create log entry
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     log_entry = f"{ip_addr} | {mac_addr} | {user_agent} | {location} | {timestamp}"

#     # Check if the log file already exists
#     if os.path.exists(log_filepath):
#         with open(log_filepath, 'a') as file:
#             file.write("================================================================================\n")
#             file.write(log_entry + "\n")
#     else:
#         with open(log_file_name, 'w') as file:
#             file.write("IP Addr | Mac Addr | User Agent | location | Timestamp\n")
#             file.write(log_entry + "\n")

#     return log_filepath




# #@auth_router.post("/token", dependencies=[Depends(RateLimiter(times=5, seconds=60))]) dependant on redis
# @auth_router.post("/token")
# #@limiter.limit("5/minute")  # Brute force protection
# async def login_for_both_access_and_refresh_tokens(request: Request, response:Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     try:
#         # Attempt to log in the user
#         user_sign_in = await login_service.log_user_in(request=request, response=response, db=db, form_data=form_data)
#         return user_sign_in

#     except HTTPException as ex:
#         if ex.status_code == status.HTTP_401_UNAUTHORIZED:
#             print("ex error: ", ex)
#             raise HTTPException(status_code=ex.status_code, detail=str(ex.detail))
#             #return Response(content=str(ex.detail), status_code=ex.status_code)
#         else:
#             # Handle specific HTTP exceptions
#             raise HTTPException(status_code=ex.status_code, detail=str(ex.detail))
#             #return Response(content=str(ex.detail), status_code=ex.status_code)

#     except RateLimitExceeded as ex:
#         # Handle rate limit exceeded
#         user = db.query(models.User).filter(models.User.username == form_data.username).first()
#         if user:
#             user.lock_account(lock_time_minutes=10)
#             db.commit()
#             info = await intruder_info(request=request)
#             log = await log_intruder_info(info.get('ip_address'), info.get('mac_address'), info.get('user_agent'), info.get('location'))

#             print("log info: ", log)
#             ###log_intruder_info(user_id=user.id, reason="Rate limit exceeded")

#         raise HTTPException(status_code=ex.status_code, detail="Account locked due to too many attempts, please try again in 10 minutes.")
#         # return Response(
#         #     content="Account locked due to too many attempts, please try again in 10 minutes.",
#         #     status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#         # )

#     except Exception as ex:
#         # Handle all other exceptions
#         print("Unexpected error in login: ", ex)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")
#         #return Response(content="An unexpected error occurred. Please try again later.", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @auth_router.get("/logged_in_users")
# async def get_logged_in_users(request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
#     online_users= login_service.list_logged_in_users(request, db, skip=skip, limit=limit)
#     print("active online users: ", online_users)
#     return online_users

# # logged_in_users_cache = []

# # def update_logged_in_users_cache(db: Session):
# #     global logged_in_users_cache
# #     # Query to list all users with active refresh tokens
# #     logged_in_users = db.query(models.User).join(models.RefreshToken, models.User.id == models.RefreshToken.user_id).all()
    
# #     # Update the global cache
# #     logged_in_users_cache = [
# #         {
# #             "username": user.username,
# #             "bio_row_id": user.bio_row_id,
# #             "email": user.email,
# #             "role_id": user.role_id
# #         }
# #         for user in logged_in_users
# #     ]
# #     print("Logged in users cache updated.")

# # @auth_router.get("/logged_in_users")
# # async def get_logged_in_users(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
# #     global logged_in_users_cache

    
# #     # Trigger the background task to update the logged-in users cache
# #     background_tasks.add_task(update_logged_in_users_cache, db)
# #     # Trigger the background task to update the logged-in users cache
# #     #background_tasks.add_task(login_service.update_logged_in_users_cache(db))
    
# #     # Return the cached list of logged-in users
# #     return {"logged_in_users": logged_in_users_cache}


# @auth_router.get("/get_cookies")
# def get_cookies(request: Request):
#     # Extract tokens from cookies
#     access_token = request.cookies.get("AccessToken")
#     refresh_token = request.cookies.get("RefreshToken")

#     return {
#         "AccessToken": access_token,
#         "RefreshToken": refresh_token
#     }



# @auth_router.post("/refresh")
# def get_new_access_token(response:Response, refresh_token: schemas.Token, db: Session = Depends(get_db)):

#     refresh_token_check = db.query(models.RefreshToken).filter(models.RefreshToken.refresh_token == refresh_token.refresh_token).first()
#     if not refresh_token_check:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
#                         detail="Could not validate new access token credentials",
#                         headers={"WWW-Authenticate": "Bearer"}
#                         )
    
#     user_data = crud.get_user(db=db, id=refresh_token_check.user_id)


#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_DURATION_IN_MINUTES)
#     new_access_token = Security.create_access_token(data={"email": user_data.email}, expires_delta=access_token_expires)
#     new_refresh_token = Security.create_refresh_token(jsonable_encoder(user_data))


#     # delete user refresh token after requesting for a new access token
#     refresh_token_check = db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user_data.id)
#     if refresh_token_check.first():
#         refresh_token_check.delete()
#         db.commit()


#     refresh_token_dict = {
#         "user_id": user_data.id,
#         "refresh_token": new_refresh_token,
#     }

#     # create new refresh token for user after requesting for a new access token
#     refresh_token_data= models.RefreshToken(**refresh_token_dict)
#     db.add(refresh_token_data)
#     db.commit()
    

#     return {
#         "access_token": new_access_token,
#         "token_type":"bearer",
#         "refresh_token":new_refresh_token,
#         "status": status.HTTP_200_OK
#         }


# @auth_router.post("/logout")
# async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
#     return await login_service.logout_user(request, response, db)


# @auth_router.get("/intruder/logs", response_class=PlainTextResponse)
# async def show_intruder_logs(date: str = None):
#     """
#     Retrieve and display intruder logs for a specified date.
#     If no date is provided, retrieve logs for the current date.
#     """

#     today = datetime.now().strftime("%Y-%m-%d")
#     if date is None:
#         date = today
        
    
#     log_filename = f"intruder_log_{date}.txt"
#     log_file_path = os.path.join("security/logs/", log_filename)
#     print("is directory exist: ", os.path.exists(log_file_path))
#     if not os.path.exists(log_file_path):
#         raise HTTPException(status_code=404, detail="Log file not found")
    
#     with open(log_file_path, "r") as log_file:
#         log_data = log_file.read()
    
#     return PlainTextResponse(log_data)


# @auth_router.get("/intruder/logs/download", response_class=FileResponse)
# async def download_intruder_log(date: str = None):
#     """
#     Query and download the intruder log file for a specific date.
#     If no date is provided, download the current date's log file.
#     """
#     today = datetime.now().strftime("%Y-%m-%d")
#     if date is None:
#         date = today
    
#     log_filename = f"intruder_log_{date}.txt"
#     log_file_path = os.path.join("security/logs/", log_filename)
    
#     if not os.path.exists(log_file_path):
#         raise HTTPException(status_code=404, detail="Log file not found")
    
#     return FileResponse(log_file_path, filename=log_filename)

#from main import log_intruder_info

# @auth_router.get("/get_intruder_list")
# def load_intruder_list(request:Request):
#     intruders = login_service.log_intruder_info(request=request)
#     return intruders


# @auth_router.get("/download-intruder-log")
# def download_intruder_log():
#     current_date = datetime.now().strftime('%Y-%m-%d')
#     log_file_name = f"security/logs/intruder_log_{current_date}.txt"

#     if os.path.exists(log_file_name):
#         return FileResponse(log_file_name, media_type='application/octet-stream', filename=log_file_name)
#     else:
#         raise HTTPException(status_code=404, detail="Log file not found.")


# @auth_router.get("/clear_intruder_list")
# def clear_intruder_list():
#     global intruder_list
#     print("before global intruder list: ", intruder_list)
#     settings.intruder_list = []
#     print(f"after global intruder list:  {intruder_list}\nsettings.intruder_list: {settings.intruder_list}")
#     return {"message": "Intruder list cleared."}
