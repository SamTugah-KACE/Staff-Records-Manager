import os
import asyncpg
from dotenv import load_dotenv
from Config.config import settings

# DATABASE_NAME = os.getenv('DATABASE_NAME')
# DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
# HOST = os.getenv('DATABASE_HOST')
# DATABASE_USER = os.getenv('DATABASE_USER')
# PORT = os.getenv('DATABASE_PORT')

DATABASE_NAME = settings.POSTGRES_DB
DATABASE_PASSWORD = settings.POSTGRES_PASSWORD
HOST = settings.POSTGRES_SERVER
DATABASE_USER = settings.POSTGRES_USER
PORT = settings.POSTGRES_PORT



async def execute_sql():
     ###using .env
    #load_dotenv(dotenv_path='Config/app.env')
    
   
    #DATABASE_NAME = settings.POSTGRES_DB
    print("DATABASE_NAME -> ",DATABASE_NAME)
    #DATABASE_PASSWORD = settings.POSTGRES_PASSWORD
    print("DATABASE_PASSWORD -> ",DATABASE_PASSWORD)
    #HOST = settings.POSTGRES_SERVER
    print("HOST -> ",HOST)
    # DATABASE_USER = settings.POSTGRES_USER
    print("DATABASE_USER -> ",DATABASE_USER)
    try:

        conn2 = await asyncpg.connect(user=f"{DATABASE_USER}", password=f"{DATABASE_PASSWORD}", database=f"{DATABASE_NAME}", host=f"{HOST}")
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
        
        
        conn = await asyncpg.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host= HOST,
            port=PORT
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
        db_name = os.getenv("DATABASE_NAME")
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


