# Use an official Python runtime as a parent image
FROM python:3.12.5-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed, 
# not supported by Nexus unfortunately
RUN apt-get update -y
RUN apt upgrade -y

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY /app .

# Expose port 8080 to the outside world
EXPOSE 8080

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
