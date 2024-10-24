from typing import List, Any
import re
from jose import JWTError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from security import Security
from models import User, RefreshToken, BioData
from database.db_session import get_db
from Config.config import settings
from fastapi.encoders import jsonable_encoder
import requests
from mail import account_emergency, send_email
import os
import json
from auth import getCurrentUserDashbaord

# intruder_list = []
class LoginService:
    
    

    # async def log_intruder_info(request: Request):
    #     client_ip = request.client.host
    #     headers = request.headers
    #     user_agent = headers.get("User-Agent")
    #     mac_address = headers.get("X-MAC-Address")  # Custom header for MAC Address
    #     location = requests.get(f"https://ipinfo.io/{client_ip}/geo").json()

    #     intruder_info = {
    #         "ip_address": client_ip,
    #         "mac_address": mac_address,
    #         "user_agent": user_agent,
    #         "location": location,
    #     }
    #     print("intruder info dict: ", intruder_info)
    #     settings.intruder_list.append(intruder_info)
    #     print(f"Intruder detected: {intruder_info}")

    # from fastapi.responses import FileResponse

    # def log_intruder_info(ip_addr: str, mac_addr: str, user_agent: str, location: str):
    #     # Get current date to create or append to the log file
    #     current_date = datetime.now().strftime('%Y-%m-%d')
    #     log_file_name = f"intruder_log_{current_date}.txt"

    #     # Create log entry
    #     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     log_entry = f"{ip_addr} | {mac_addr} | {user_agent} | {location} | {timestamp}"

    #     # Check if the log file already exists
    #     if os.path.exists(log_file_name):
    #         with open(log_file_name, 'a') as file:
    #             file.write("==========================\n")
    #             file.write(log_entry + "\n")
    #     else:
    #         with open(log_file_name, 'w') as file:
    #             file.write("IP Addr | Mac Addr | User Agent | location | Timestamp\n")
    #             file.write(log_entry + "\n")


    def get_tokens(self, request: Request):
        # Extract tokens from cookies
        access_token = request.cookies.get("AccessToken")
        refresh_token = request.cookies.get("RefreshToken")
        print("access token from cookies: ", access_token)
        print("refresh token from cookies: ", refresh_token)
        return {
            "AccessToken": access_token,
            "RefreshToken": refresh_token
        }
    

    def list_logged_in_users(self,  request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100) :
        
        
        # Fetch tokens from cookies
        tokens = login_service.get_tokens(request)

        if not tokens['AccessToken'] or not tokens['RefreshToken']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

        user_email = None

        # Verify Access Token
        try:
            payload = Security.decode_token(tokens['AccessToken'])
            user_email = payload.get("sub")
        except JWTError:
            # If Access Token is invalid, try verifying the Refresh Token
            try:
                payload = Security.decode_token(tokens['RefreshToken'])
                user = payload.get("sub")
                if user:
                    user_email = user.email  # Extract email from user object
            except JWTError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid tokens")

        if not user_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to determine logged-in user")

        # Query to list all users with active refresh tokens
        logged_in_users = db.query(User).join(RefreshToken, User.id == RefreshToken.user_id).offset(skip).limit(limit).all()

        # Format the output
        user_list = [
            {
                "username": user.username,
                "bio_row_id": user.bio_row_id,
                "email": user.email,
                "role": user.role
            }
            for user in logged_in_users
        ]

        return {"logged_in_users": user_list}


    logged_in_users_cache = []

    def update_logged_in_users_cache(db: Session):
        global logged_in_users_cache
        # Query to list all users with active refresh tokens
        logged_in_users = db.query(User).join(RefreshToken, User.id == RefreshToken.user_id).all()
        
        # Update the global cache
        logged_in_users_cache = [
            {
                "username": user.username,
                "bio_row_id": user.bio_row_id,
                "email": user.email,
                "role_id": user.role_id
            }
            for user in logged_in_users
        ]
        print("Logged in users cache updated.")

    # def log_intruder_info(intruder_info: dict):
    #     current_date = datetime.now().strftime('%Y-%m-%d')
    #     log_file_name = f"intruder_log_{current_date}.txt"
    #     log_directory = "security/logs/"

    #     os.makedirs(log_directory, exist_ok=True)
    #     log_filepath = os.path.join(log_directory, log_file_name)

    #     log_entry = (
    #         f"Timestamp: {intruder_info['timestamp']}\n"
    #         f"IP Address: {intruder_info['ip_address']}\n"
    #         f"MAC Address: {intruder_info['mac_address']}\n"
    #         f"User-Agent: {intruder_info['user_agent']}\n"
    #         f"Location: {intruder_info['location']}\n"
    #         f"Username Attempted: {intruder_info['username']}\n"
    #         f"Password Attempted: {intruder_info['password']}\n"
    #         "==========================\n"
    #     )

    #     with open(log_filepath, "a") as log_file:
    #         log_file.write(log_entry)

    
    # def log_intruder_attempt(self, username: str, password: str, request: Request):
    #     intruder_info = {
    #         "username": username,
    #         "password": password,
    #         "ip_address": request.client.host,
    #         "mac_address": request.headers.get("X-MAC-Address"),
    #         "user_agent": request.headers.get("User-Agent"),
    #         "location": requests.get(f"https://ipinfo.io/{request.client.host}/geo").json(),
    #         "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     }
        
    #     # Log the intruder information
    #     self.log_intruder_info(intruder_info)

    #########################################################################

    def secure_log_intruder_info(self, intruder_info: dict):
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file_name = f"intruder_log_{current_date}.txt"
        log_directory = "security/logs/"

        # Secure the logging directory
        #os.makedirs(log_directory, mode=0o750, exist_ok=True)
        os.makedirs(log_directory,  exist_ok=True)
        log_filepath = os.path.join(log_directory, log_file_name)

        print("log directory: ", log_filepath)

        log_entry = (
            f"Timestamp: {intruder_info.get('timestamp', 'N/A')}\n"
            f"IP Address: {intruder_info.get('ip_address', 'N/A')}\n"
            f"MAC Address: {intruder_info.get('mac_address', 'N/A')}\n"
            f"User-Agent: {intruder_info.get('user_agent', 'N/A')}\n"
            f"Location: {json.dumps(intruder_info.get('location', {}))}\n"
            f"Username Attempted: {intruder_info.get('username', 'N/A')}\n"
            "\n================================================================================\n\n"
        )

        # Use a try-except block to catch potential errors
        try:
            with open(log_filepath, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
            
            print(f"successfully log intruder's info.\ninfo: {log_entry}")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    #get location data
    async def get_location_data(self, ip_address: str) -> dict:
        try:
            response = await requests.get(f"https://ipinfo.io/{ip_address}/geo")
            if response.status_code == 200:
                return response.json()
            
            print("intruder's location identified: ", response.json())
        except Exception as e:
            print(f"Error fetching location data: {e}")
        return {}
    
    
    async def log_intruder_attempt(self, username: str, request: Request):
        # try:
        #     print("finding device location...")
        #     # Asynchronous request to get location data
        #     await LoginService.get_location_data(self, request.client.host)
        #     #print("\nlocation: ", location)
        #     #return location
        # except Exception as e:
        #     print(f"Error fetching location data: {e}")
        #     location = {}

        location = {}
        try:
            response = requests.get(f"https://ipinfo.io/{request.client.host}/geo")
            if response.status_code == 200:
                print("response success: ", response)
                location = response.json()
                #return response.json()
            print("response location: ", response)
            print("intruder's location identified: ", response.json())
        except Exception as e:
            print(f"Error fetching location data: {e}")
        #return {}
        print("location: ", location)
        intruder_info = {
            "username": username,
            "ip_address": request.client.host,
            "mac_address": request.headers.get("X-MAC-Address", "N/A"),
            "user_agent": request.headers.get("User-Agent", "N/A"),
            "location": location,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Log the intruder information
        return LoginService.secure_log_intruder_info(self,intruder_info)


    async def log_user_in(self, request:Request, response: Response, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
        user = db.query(User).filter(User.username == form_data.username).first()
        print("user in log: ", user.failed_login_attempts)
        print("user account locked until: ", user.account_locked_until)
        print("is user account blocked? ", user.is_account_locked())

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account Disabled, please contact system administrator for redress.",
            )
        # Ensure datetime.now() is timezone-aware by setting it to UTC
        now_utc = datetime.now(timezone.utc)
        print("now_utc: ", now_utc)
        if user.is_account_locked():
            if now_utc < user.account_locked_until:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is locked due to multiple failed login attempts.",
                )
            else:
                # Unlock the account if the lock time has passed
                #user.reset_failed_attempts()
                user.account_locked_until = None
                db.commit()

        if not Security.verify_password(form_data.password, user.hashed_password):
            user.failed_login_attempts += 1
            print("Failed login attempts incremented to:", user.failed_login_attempts)

            if user.failed_login_attempts >= 5:
                user.lock_account(lock_time_minutes=10)
                if user.lock_count <= 2:
                    user.lock_count += 1
                elif user.lock_count >= 3:
                    user.is_active = False
                    user.lock_count = 0
                    db.commit()
                    email_body = account_emergency()
                    await send_email(email=user.email, subject="Account Status", body=email_body)  #send email message
                
                print("lock count = ", user.lock_count)    
                db.commit()
                
                await LoginService.log_intruder_attempt(self, user.username, request)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is locked due to multiple failed login attempts.",
                )
            
            db.commit()
            #await LoginService.log_intruder_attempt(self, user.username, request)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        # Reset failed attempts after successful login
        user.reset_failed_attempts()
        db.commit()
        
        # Token creation logic
        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(seconds=settings.REFRESH_TOKEN_DURATION_IN_MINUTES)
        
        if form_data.scopes and "remember_me" in form_data.scopes:
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_REMEMBER_ME_DAYS)

        access_token = Security.create_access_token(
            data={"sub": str(user.username)}, expires_delta=access_token_expires
        )
        refresh_token = Security.create_refresh_token(
            data={"sub": str(user)}, expires_delta=refresh_token_expires
        )


        expiration_time = datetime.now() + refresh_token_expires
        access_token_expiration = datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        db_refresh_token = db.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
        if db_refresh_token:
            db_refresh_token.refresh_token = refresh_token
            db_refresh_token.expiration_time = expiration_time
        else:
            db_refresh_token = RefreshToken(user_id=user.id, refresh_token=refresh_token, expiration_time=expiration_time)
            db.add(db_refresh_token)

        db.commit()

        # Set cookies for access and refresh tokens
        # response.set_cookie(key="AccessToken", value=access_token, httponly=True, secure=False, samesite='none', expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        

        is_production = os.getenv("ENV") == "production"
        print("is_production: ", is_production)
        response.set_cookie(
            key="AccessToken",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production, False in development
            samesite='none' if is_production else 'lax',  # Use lax in dev for non-HTTPS
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )




        if form_data.scopes and "remember_me" in form_data.scopes:
            response.set_cookie(key="RefreshToken", value=refresh_token, httponly=True, secure=True, samesite='none', expires=(settings.REFRESH_TOKEN_DURATION_IN_MINUTES+settings.REFRESH_TOKEN_DURATION_IN_MINUTES))
        else:
            response.set_cookie(key="RefreshToken", value=refresh_token, httponly=True, secure=True, samesite='none', expires=settings.REFRESH_TOKEN_DURATION_IN_MINUTES)

        dash = getCurrentUserDashbaord(user, db)
        print("dashboard -> ", dash)
        bio = db.query(BioData).filter(BioData.id == user.bio_row_id).first()
        print("\nuser bio-data: ", bio)
        fullname = ""
        if bio:
            fullname = f"{bio.title} {bio.first_name} {bio.surname} {bio.other_names or ''}"
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "access_token_expiration": access_token_expiration,
            "user": {
                "id": user.id, 
                "bio_row_id": user.bio_row_id,
                "welcome": fullname + f" ({user.role})",
                "email": user.email,
                "role": user.role,
                "dashboard": dash
            },
            "refresh_token": refresh_token,
            "refresh_token_expiration": expiration_time
        }



    async def logout_user(self, request: Request, response: Response, db: Session = Depends(get_db)):
        # Retrieve the AccessToken from the Authorization header
        authorization: str = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
        
        # Extract the token from the Authorization header
        access_token = authorization.split(" ")[1]

        # Verify the access token
        try:
            payload = Security.decode_token(access_token)
            user_email = payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid tokens")

        if not user_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to determine logged-in user")
        
        print("username from payload token: ", user_email)

        # Retrieve the user from the database
        user = db.query(User).filter(User.username == user_email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        # Retrieve the user's refresh token
        refresh_token = db.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found")

        # Invalidate the refresh token
        refresh_token.expiration_time = datetime.now(timezone.utc)
        db.commit()

        # Return a success message (no cookies to clear since tokens are stored in localStorage)
        return {"status": "logged out successfully"}


    # async def logout_user(self, request: Request, response: Response, db: Session = Depends(get_db)):
    #     tokens = login_service.get_tokens(request)
    #     if not tokens['AccessToken'] or not tokens['RefreshToken']:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
        
    #     # Verify the refresh token
    #     try:
    #         payload = Security.decode_token(tokens['AccessToken'])
    #         user_email = payload.get("sub")
    #     except JWTError:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid tokens")

    #     if not user_email:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to determine logged-in user")
        
    #     print("email from payload token: ", user_email)
    #     # Retrieve the user's refresh token
    #     user = db.query(User).filter(User.email == user_email).first()
    #     if not user:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    #     refresh_token = db.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
    #     if not refresh_token:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found")

    #     # Invalidate the token by setting the logged_out_at timestamp
    #     # refresh_token.logged_out_at = datetime.now()
    #     # db.commit()

    #     refresh_token.expiration_time = datetime.now(timezone.utc)  # Invalidate the token
    #     db.commit()

    #     # Clear tokens from the cookies
    #     response.delete_cookie(key="AccessToken")
    #     response.delete_cookie(key="RefreshToken")

    #     return {"status": "logged out successfully"}
    

    


  




login_service = LoginService()