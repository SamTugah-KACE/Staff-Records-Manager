import os
import asyncpg
from dotenv import load_dotenv
from Config.config import settings

# DATABASE = os.getenv('DATABASE')
# DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
# HOST = os.getenv('DATABASE_HOST')
# USER = os.getenv('USER')
# PORT = os.getenv('DATABASE_PORT')

# DATABASE = settings.DATABASE
# DATABASE_PASSWORD = settings.DATABASE_PASSWORD
# HOST = settings.DATABASE_HOST
# USER = settings.USER
# PORT = settings.DATABASE_PORT
 



#load_dotenv(dotenv_path='Config/app.env')



async def execute_sql():
     ###using .env
    HOST = os.getenv("DATABASE_HOST")
    PORT = os.getenv("DATABASE_PORT")
    DBUSER = os.getenv("DB_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE = os.getenv("DATABASE")


    #DATABASE = settings.POSTGRES_DB
    print("DATABASE -> ",DATABASE)
    #DATABASE_PASSWORD = settings.POSTGRES_PASSWORD
    print("DATABASE_PASSWORD -> ",DATABASE_PASSWORD)
    #HOST = settings.POSTGRES_SERVER
    print("HOST -> ",HOST)
    # USER = settings.POSTGRES_USER
    print("USER -> ",DBUSER)
    try:

        conn2 = await asyncpg.connect(user=f"{DBUSER}", password=f"{DATABASE_PASSWORD}", database=f"{DATABASE}", host=f"{HOST}")
        print("conn2: ", conn2)
        db_sql_path = os.path.join(os.path.dirname(__file__), "db.sql")
        
        if os.path.exists(db_sql_path):
            # Read the SQL file
            with open(db_sql_path, 'r') as file:
                sql_commands = file.read()

            # Create extension if not exists
            await conn2.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

                # Execute the SQL commands
            await conn2.execute(sql_commands)
            print(f"SQL script '{db_sql_path}' executed successfully.")
        await conn2.close()

        return True
    
    except Exception as error:
        print("Error executing SQL file:", error)
        return False



async def check_and_create_database():
    """
    Check if a PostgreSQL database exists, if not, create the database and execute a SQL script.

    Args:
        db_name (str): The name of the PostgreSQL database.
        db_sql_path (str): The path to the SQL script to execute.

    Returns:
        bool: True if the database exists or is created successfully, False otherwise.
    """
   
    try:
        print("\nin sec func")
        print("user: ", os.getenv("DB_USER"))
        #DATABASE = settings.POSTGRES_DB
        print("DATABASE -> ",os.getenv("DATABASE"))
        #DATABASE_PASSWORD = settings.POSTGRES_PASSWORD
        print("DATABASE_PASSWORD -> ",os.getenv("DATABASE_PASSWORD"))
        #HOST = settings.POSTGRES_SERVER
        print("HOST -> ",os.getenv("DATABASE_HOST"))
        #USER = settings.POSTGRES_USER
        print("PORT -> ",os.getenv("DATABASE_PORT"))
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            host= os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT")
        )
        print("conn -> ", conn)
        # conn = await asyncpg.connect(
        #     user=settings.POSTGRES_USER,
        #     password=settings.POSTGRES_PASSWORD,
        #     host=settings.POSTGRES_SERVER,
        #     port=settings.POSTGRES_PORT
        # )
        
        # Connect to PostgreSQL server
        
        # Connect to PostgreSQL server
        db_name = os.getenv("DATABASE")
        #db_name =settings.POSTGRES_DB
        
        
        # Check if the database exists
        db_exists = await conn.fetchval(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        print("db exists: ", db_exists)
        if not db_exists:
            # Create the database if it doesn't exist
            await conn.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
            await conn.close()
            await execute_sql()
           

        return True
    
    except Exception as error:
        print("Error while connecting to PostgreSQL:", error)
        return False


