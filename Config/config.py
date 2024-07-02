import secrets
import os
 
#from dotenv import load_dotenv

#load_dotenv(dotenv_path='CONFIG/conf.env')

class Settings:
    PROJECT_NAME:str = "Personal Records Form"
    PROJECT_VERSION: str = "1.0.0"

   

    SMS_API_KEY:str  = os.getenv("ARKESEL_API_KEY")
    SMS_API_URL: str = os.getenv("ARKESEL_BASE_URL")
    

    MAX_CONCURRENT_THREADS: int = 10  # Maximum number of concurrent threads
    MAX_RETRIES: int = 1  # Maximum number of retry attempts
    RETRY_DELAY_BASE: int = 0  # Initial retry delay in seconds
    RETRY_DELAY_MULTIPLIER: int = 1  # Exponential backoff multiplier


    #set_allow_origin = ['http://localhost:4200','https://smconf.gikace.dev', 'https://smconf-test.web.app']

    set_allow_origin = "http://localhost:4200,https://smconf.gikace.dev, https://smconf-test.web.app"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "1234")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "personal_records_db")
    INSTANCE_CONNECTION_NAME: str = os.getenv("INSTANCE_CONNECTION_NAME", None)
    UNIX_SOCKET: str = os.getenv("INSTANCE_UNIX_SOCKET", '/cloudsql/')
    PROJECT_ID: str = os.getenv("PROJECT_ID")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME", "personal_records_app")
    FLYER_PATH: str = os.getenv("FLYER_PATH")
    OUTLINE_PATH: str = os.getenv("OUTLINE_PATH")
    SHOW_DOCS: str = os.getenv("SHOW_DOCS")
    ALLOW_ORIGINS: str = os.getenv("ALLOW_ORIGINS", set_allow_origin)
    SET_NEW_ORIGIN : list = ALLOW_ORIGINS.split(',')




    SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

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