import os
import asyncpg
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv(dotenv_path='Config/app.env')

async def get_db_connection_params():
    """
    Extracts and returns PostgreSQL connection parameters from the DATABASE_URL environment variable.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not found.")

    # Parse the DATABASE_URL (expected format: postgres://user:password@host:port/dbname)
    parsed_url = urlparse(database_url)

    return {
        "user": parsed_url.username,
        "password": parsed_url.password,
        "host": parsed_url.hostname,
        "port": parsed_url.port or 5432,
        "database": parsed_url.path[1:],  # Removes the leading '/'
    }

async def get_connection_pool():
    """
    Set up a connection pool to the PostgreSQL database.
    Connection pooling allows multiple connections to be managed efficiently.
    """
    conn_params = await get_db_connection_params()

    try:
        pool = await asyncpg.create_pool(
            user=conn_params["user"],
            password=conn_params["password"],
            database=conn_params["database"],
            host=conn_params["host"],
            port=conn_params["port"],
            ssl="require",  # Ensure SSL connection
            max_size=10,  # Adjust pool size based on expected load
            min_size=1
        )
        return pool
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        raise

async def execute_sql(pool):
    """
    Execute the db.sql file to set up the database schema using a connection pool.
    """
    try:
        # Path to the SQL file
        db_sql_path = os.path.join(os.path.dirname(__file__), "db.sql")

        # Check if the SQL file exists
        if os.path.exists(db_sql_path):
            with open(db_sql_path, 'r') as file:
                sql_commands = file.read()

            # Use a connection from the pool to execute SQL commands
            async with pool.acquire() as conn:
                # Create extension if not exists (for UUID support)
                await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
                await conn.execute(sql_commands)
                print(f"SQL script '{db_sql_path}' executed successfully.")
            return True
        else:
            print(f"SQL file '{db_sql_path}' does not exist.")
            return False

    except Exception as error:
        print(f"Error executing SQL file: {error}")
        return False

async def check_and_create_database():
    """
    Check if a PostgreSQL database exists, and if not, execute the db.sql script.
    """
    try:
        pool = await get_connection_pool()
        database_name = (await get_db_connection_params())['database']

        # Use a connection from the pool to check for the database and its tables
        async with pool.acquire() as conn:
            # Check if the database has any tables in the public schema
            table_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public')"
            )

            if table_exists:
                print(f"Database '{database_name}' already has tables. Skipping SQL execution.")
            else:
                print(f"Database '{database_name}' exists but has no tables. Executing SQL script.")
                await execute_sql(pool)

        # Close the connection pool
        await pool.close()
        return True

    except Exception as error:
        print(f"Error while checking/creating database: {error}")
        return False








# # import database.setup
# # import os
# # import asyncpg
# # from dotenv import load_dotenv
# # from Config.config import settings

# # # DATABASE = os.getenv('DATABASE')
# # # DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
# # # HOST = os.getenv('DATABASE_HOST')
# # # USER = os.getenv('USER')
# # # PORT = os.getenv('DATABASE_PORT')

# # # DATABASE = settings.DATABASE
# # # DATABASE_PASSWORD = settings.DATABASE_PASSWORD
# # # HOST = settings.DATABASE_HOST
# # # USER = settings.USER
# # # PORT = settings.DATABASE_PORT
 



# # #load_dotenv(dotenv_path='Config/app.env')



# # async def execute_sql():
# #      ###using .env
# #     HOST = os.getenv("DATABASE_HOST")
# #     PORT = os.getenv("DATABASE_PORT")
# #     DBUSER = os.getenv("DB_USER")
# #     DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
# #     DATABASE = os.getenv("DATABASE")


# #     #DATABASE = settings.POSTGRES_DB
# #     print("DATABASE -> ",DATABASE)
# #     #DATABASE_PASSWORD = settings.POSTGRES_PASSWORD
# #     print("DATABASE_PASSWORD -> ",DATABASE_PASSWORD)
# #     #HOST = settings.POSTGRES_SERVER
# #     print("HOST -> ",HOST)
# #     # USER = settings.POSTGRES_USER
# #     print("USER -> ",DBUSER)
# #     try:

# #         conn2 = await asyncpg.connect(user=f"{DBUSER}", password=f"{DATABASE_PASSWORD}", database=f"{DATABASE}", host=f"{HOST}")
# #         print("conn2: ", conn2)
# #         db_sql_path = os.path.join(os.path.dirname(__file__), "db.sql")
        
# #         if os.path.exists(db_sql_path):
# #             # Read the SQL file
# #             with open(db_sql_path, 'r') as file:
# #                 sql_commands = file.read()

# #             # Create extension if not exists
# #             await conn2.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

# #                 # Execute the SQL commands
# #             await conn2.execute(sql_commands)
# #             print(f"SQL script '{db_sql_path}' executed successfully.")
# #         await conn2.close()

# #         return True
    
# #     except Exception as error:
# #         print("Error executing SQL file:", error)
# #         return False



# # async def check_and_create_database():
# #     """
# #     Check if a PostgreSQL database exists, if not, create the database and execute a SQL script.

# #     Args:
# #         db_name (str): The name of the PostgreSQL database.
# #         db_sql_path (str): The path to the SQL script to execute.

# #     Returns:
# #         bool: True if the database exists or is created successfully, False otherwise.
# #     """
   
# #     try:
# #         print("\nin sec func")
# #         print("user: ", os.getenv("DB_USER"))
# #         #DATABASE = settings.POSTGRES_DB
# #         print("DATABASE -> ",os.getenv("DATABASE"))
# #         #DATABASE_PASSWORD = settings.POSTGRES_PASSWORD
# #         print("DATABASE_PASSWORD -> ",os.getenv("DATABASE_PASSWORD"))
# #         #HOST = settings.POSTGRES_SERVER
# #         print("HOST -> ",os.getenv("DATABASE_HOST"))
# #         #USER = settings.POSTGRES_USER
# #         print("PORT -> ",os.getenv("DATABASE_PORT"))
# #         conn = await asyncpg.connect(
# #             user=os.getenv("DB_USER"),
# #             password=os.getenv("DATABASE_PASSWORD"),
# #             host= os.getenv("DATABASE_HOST"),
# #             port=os.getenv("DATABASE_PORT")
# #         )

        
# #         print("conn -> ", conn)
# #         # conn = await asyncpg.connect(
# #         #     user=settings.POSTGRES_USER,
# #         #     password=settings.POSTGRES_PASSWORD,
# #         #     host=settings.POSTGRES_SERVER,
# #         #     port=settings.POSTGRES_PORT
# #         # )
        
# #         # Connect to PostgreSQL server
        
# #         # Connect to PostgreSQL server
# #         db_name = os.getenv("DATABASE")
# #         #db_name =settings.POSTGRES_DB
        
        
# #         # Check if the database exists
# #         db_exists = await conn.fetchval(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
# #         print("db exists: ", db_exists)
# #         if not db_exists:
# #             # Create the database if it doesn't exist
# #             await conn.execute(f"CREATE DATABASE {db_name}")
# #             print(f"Database '{db_name}' created successfully.")
# #             await conn.close()
# #             await execute_sql()
# #         else:
# #             print("db already created: ", db_name)
# #             await execute_sql()
           

# #         return True
    
# #     except Exception as error:
# #         print("Error while connecting to PostgreSQL:", error)
# #         #await execute_sql()
# #         #conn2 = await asyncpg.connect(user=os.getenv("DB_USER"), password=os.getenv("DATABASE_PASSWORD"), database=os.getenv("DATABASE"), host=os.getenv("DATABASE_HOST"))
# #         #print("conn2: ", conn2)
# #         return False

# import os
# import asyncpg
# from dotenv import load_dotenv


# #load_dotenv(dotenv_path='Config/app.env')

# async def execute_sql():
#     HOST = os.getenv("DATABASE_HOST")
#     PORT = os.getenv("DATABASE_PORT")
#     DBUSER = os.getenv("DB_USER")
#     DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
#     DATABASE = os.getenv("DATABASE")

#     print("DATABASE -> ",DATABASE)

#     print("execute sql dbuser: ", DBUSER)
#     try:
#         conn = await asyncpg.connect(user=DBUSER, password=DATABASE_PASSWORD, database=DATABASE, host=HOST)
#         db_sql_path = os.path.join(os.path.dirname(__file__), "db.sql")

#         if os.path.exists(db_sql_path):
#             with open(db_sql_path, 'r') as file:
#                 sql_commands = file.read()

#             await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
#             await conn.execute(sql_commands)
#             print(f"SQL script '{db_sql_path}' executed successfully.")

#         await conn.close()
#         return True

#     except Exception as error:
#         print("Error executing SQL file:", error)
#         return False

# async def check_and_create_database():
#     try:
#         HOST = os.getenv("DATABASE_HOST")
#         PORT = os.getenv("DATABASE_PORT")
#         DBUSER = os.getenv("DB_USER")
#         DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
#         DATABASE = os.getenv("DATABASE")

#         print(f"""  
#             Host: {HOST}\n
#             Port: {PORT}\n
#             DBUSER: {DBUSER}\n
#             DATABASE PASSWORD: {DATABASE_PASSWORD}\n
#             DATABASE: {DATABASE}
#         """)
#         conn = await asyncpg.connect(
#             user=DBUSER,
#             password=DATABASE_PASSWORD,
#             host=HOST,
#             port=PORT
#         )
#         print("connection successful: ", conn)
#         # Check if the database exists
#         db_exists = await conn.fetchval(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DATABASE}'")
#         print("database exists? ", db_exists)
#         if not db_exists:
#             await conn.execute(f"CREATE DATABASE {DATABASE}")
#             print(f"Database '{DATABASE}' created successfully.")
#             await conn.close()
#             await execute_sql()
#         else:
#             # Connect to the existing database to check for tables
#             await conn.close()
#             conn = await asyncpg.connect(user=DBUSER, password=DATABASE_PASSWORD, database=DATABASE, host=HOST)
#             print("db exist, let's check tables.\nnew connection: ",conn)
#             table_exists = await conn.fetchval(
#                 "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public')"
#             )
#             print("tables exist? ", table_exists)
#             if table_exists:
#                 print(f"Database '{DATABASE}' already has tables. Skipping SQL execution.")
#             else:
#                 print(f"Database '{DATABASE}' exists but has no tables. Executing SQL script.")
#                 await execute_sql()

#             await conn.close()

#         return True

#     except Exception as error:
#         print("Error while connecting to PostgreSQL:", error)
#         return False

