# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY ./app /app/app

# Make port 8000 available to the world outside this container
# (Cloud Run and other services expect apps to listen on $PORT, often 8080 or 8000)
EXPOSE 8000

# Define environment variable (optional, can be overridden)
ENV APP_MODULE="app.main:app"
ENV HOST="0.0.0.0"
ENV PORT="8000"

# Run app.main:app when the container launches
# Use Gunicorn for a production-ready server, or Uvicorn for simplicity/development
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Using Gunicorn (recommended for more robust production deployments with Uvicorn workers)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]

# If you need to ensure scripts are executable or set other permissions:
# RUN chmod +x /app/start-server.sh # If you use a startup script 