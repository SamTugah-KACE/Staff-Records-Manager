# Use an official Python runtime as a parent image
ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION} as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Install system dependencies
#RUN apt-get update && apt-get install -y libgl1-mesa-glx
# RUN apt-get update && apt-get install -y \
#     libgl1-mesa-glx \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install dependencies with cache optimization
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-it.sh script
#COPY wait-for-it.sh /wait-for-it.sh

# Ensure the wait-for-it.sh script is executable
#RUN chmod +x /wait-for-it.sh

# Copy the rest of the source code into the container
COPY . .

# Ensure the upload directory exists and has appropriate permissions
RUN mkdir -p ./uploads/images/ && chmod -R 755 ./uploads/images/
RUN mkdir -p ./downloads/documents/  && chmod -R 755 ./downloads/documents/

# Expose the port that the application listens on
EXPOSE 8080

# Run the application with wait-for-it.sh to wait for the database
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
#CMD ["./wait-for-it.sh", "auth_sys:5432", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# Run Alembic migrations before starting the app
#CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]



# Comments are provided throughout this file to help you get started.
# # If you need more help, visit the Dockerfile reference guide at
# # https://docs.docker.com/engine/reference/builder/

# ARG PYTHON_VERSION=3.12.2
# FROM python:${PYTHON_VERSION} as base

# # Prevents Python from writing pyc files.
# ENV PYTHONDONTWRITEBYTECODE=1

# # Keeps Python from buffering stdout and stderr to avoid situations where
# # the application crashes without emitting any logs due to buffering.
# ENV PYTHONUNBUFFERED=1

# # Install system dependencies
# RUN apt-get update && apt-get install -y libgl1-mesa-glx
#     # build-essential \
#     # libpq-dev \
#     # libgl1-mesa-glx \
#     # libglib2.0-0 \
#     # && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Copy requirements.txt into the container
# COPY requirements.txt .

# # Install dependencies with verbose logging to diagnose potential issues
# #RUN pip install --no-cache-dir -r requirements.txt --log /tmp/pip_log.txt || (cat /tmp/pip_log.txt && false)
# #RUN pip install --no-cache-dir -r requirements.txt 
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

# # Copy the source code into the container
# COPY . .

# # Ensure the dataset directory exists and has appropriate permissions
# RUN mkdir -p ./dataset && chmod -R 755 ./dataset

# # Expose the port that the application listens on
# EXPOSE 8080

# # Run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]



# # Backend/Dockerfile

# # ARG PYTHON_VERSION=3.12.2
# # FROM python:${PYTHON_VERSION} as base

# # # Prevents Python from writing pyc files.
# # ENV PYTHONDONTWRITEBYTECODE=1

# # # Keeps Python from buffering stdout and stderr
# # ENV PYTHONUNBUFFERED=1

# # WORKDIR /app

# # # Install system dependencies (uncomment if necessary)
# # #RUN apt-get update && apt-get install -y libgl1-mesa-glx

# # # Copy requirements file and install dependencies
# # COPY requirements.txt .
# # RUN pip install --no-cache-dir -r requirements.txt

# # # Copy the source code into the container
# # COPY . .

# # # Expose the port that the application listens on
# # EXPOSE 8080

# # # Run the application
# # CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]