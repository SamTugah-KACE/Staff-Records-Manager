import secrets
import os
 
#from dotenv import load_dotenv

#load_dotenv(dotenv_path='CONFIG/conf.env')

class Settings:
    PROJECT_NAME:str = "GI-KACE Staff Records Management System"
    PROJECT_VERSION: str = "1.0.0"

   

    SMS_API_KEY:str  = os.getenv("ARKESEL_API_KEY")
    SMS_API_URL: str = os.getenv("ARKESEL_BASE_URL")
    

    MAX_CONCURRENT_THREADS: int = 10  # Maximum number of concurrent threads
    MAX_RETRIES: int = 1  # Maximum number of retry attempts
    RETRY_DELAY_BASE: int = 0  # Initial retry delay in seconds
    RETRY_DELAY_MULTIPLIER: int = 1  # Exponential backoff multiplier

    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "sam_tugah_kace")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "vjIDmbKK2KNpFm8h64JgK7jKW9bTpxP5")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "dpg-cqrmj3ggph6c73a1u4k0-a")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "staff_records_db")
    
    # POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    # POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    # POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    # POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    # POSTGRES_DB: str = os.getenv("POSTGRES_DB", "staff_records_db")






    # POSTGRES_USER: str = os.getenv("POSTGRES_USER", "sam_tugah_kace")
    # POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "vjIDmbKK2KNpFm8h64JgK7jKW9bTpxP5")
    # POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "dpg-cqrmj3ggph6c73a1u4k0-a")
    # POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    # POSTGRES_DB: str = os.getenv("POSTGRES_DB", "staff_records_db")


    SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    DATABASE_HOST: str=os.getenv("DATABASE_HOST", "dpg-cqrmj3ggph6c73a1u4k0-a")
    DATABASE_PORT: str=os.getenv("DATABASE_PORT",5432)
    DBUSER: str=os.getenv("DB_USER","sam_tugah_kace")
    DATABASE_PASSWORD: str=os.getenv("DATABASE_PASSWORD","vjIDmbKK2KNpFm8h64JgK7jKW9bTpxP5")
    DATABASE: str=os.getenv("DATABASE","staff_records_db")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL","postgresql://sam_tugah_kace:vjIDmbKK2KNpFm8h64JgK7jKW9bTpxP5@dpg-cqrmj3ggph6c73a1u4k0-a/staff_records_db")

    
    # DATABASE_HOST: str=os.getenv("DATABASE_HOST", "dpg-cqrmj3ggph6c73a1u4k0-a")
    # DATABASE_PORT: str=os.getenv("DATABASE_PORT",5432)
    # USER: str=os.getenv("USER","sam_tugah_kace")
    # DATABASE_PASSWORD: str=os.getenv("DATABASE_PASSWORD","vjIDmbKK2KNpFm8h64JgK7jKW9bTpxP5")
    # DATABASE: str=os.getenv("DATABASE","staff_records_db")
    # DATABASE_URL: str = os.getenv("DATABASE_URL","postgresql://sam_tugah_kace:vjIDmbKK2KNpFm8h64JgK7jKW9bTpxP5@dpg-cqrmj3ggph6c73a1u4k0-a/staff_records_db")

    MySQL_USER: str = os.getenv("MySQL_USER", "samuelkusiduahAI")
    MySQL_PASSWORD: str = os.getenv("MySQL_PASSWORD", "password_80")
    MySQL_SERVER: str = os.getenv("MySQL_SERVER", "samuelkusiduahAITI.mysql.pythonanywhere-services.com")
    MySQL_PORT: str = os.getenv("MySQL_PORT", 5432)
    MySQL_DB: str = os.getenv("MySQL_DB", "samuelkusiduahAI$personal_records_db")

    #DATABASE_URL = f"mysql+aiomysql://{MySQL_USER}:{MySQL_PASSWORD}@{MySQL_SERVER}/{MySQL_DB}"

    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "dev.aiti.com.gh@gmail.com")
    MAIL_PORT: str = os.getenv("MAIL_PORT")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", False)
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True


    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://smconf-test.web.app")


    EMAIL_CODE_DURATION_IN_MINUTES: int = 15
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 45
    REFRESH_TOKEN_DURATION_IN_MINUTES: int =  2592000
    COOKIE_ACCESS_EXPIRE = 1800
    COOKIE_REFRESH_EXPIRE = 2592000 # 1 Month
    COOKIE_DOMAIN: str = os.getenv("COOKIE_DOMAIN", "gikace.dev")
    PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES: int = 15
    ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES: int = 15
    

    POOL_SIZE: int = 20
    POOL_RECYCLE: int = 3600
    POOL_TIMEOUT: int = 15
    MAX_OVERFLOW: int = 2
    CONNECT_TIMEOUT: int = 60
    connect_args = {"connect_timeout":CONNECT_TIMEOUT}

    JWT_SECRET_KEY : str = secrets.token_urlsafe(32)
    REFRESH_TOKEN_SECRET_KEY : str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    COOKIE_REFRESH_EXPIRE = 290500



    # EMAIL_CODE_DURATION_IN_MINUTES: int = os.getenv("EMAIL_CODE_DURATION_IN_MINUTES")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    # REFRESH_TOKEN_DURATION_IN_MINUTES: int = os.getenv("REFRESH_TOKEN_DURATION_IN_MINUTES")
    # PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES: int = os.getenv("PASSWORD_RESET_TOKEN_DURATION_IN_MINUTES")
    # ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES: int = os.getenv("ACCOUNT_VERIFICATION_TOKEN_DURATION_IN_MINUTES")

    # POOL_SIZE: int = os.getenv("POOL_SIZE")
    # POOL_RECYCLE: int = os.getenv("POOL_RECYCLE")
    # POOL_TIMEOUT: int = os.getenv("POOL_TIMEOUT")
    # MAX_OVERFLOW: int = os.getenv("MAX_OVERFLOW")
    # CONNECT_TIMEOUT: int = os.getenv("CONNECT_TIMEOUT")
    # connect_args = {"connect_timeout":os.getenv("CONNECT_TIMEOUT")}



    # JWT_SECRET_KEY : str = os.getenv("JWT_SECRET_KEY")
    # ALGORITHM: str = os.getenv("ALGORITHM")

    # class Config:


    #     env_file = './.env'

settings = Settings()
