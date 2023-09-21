# Use a minimal base image
FROM python:3.9

# Set non-root user and group with a home directory
RUN groupadd -r myuser && useradd -r -m -g myuser myuser

# Set the working directory within the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY counter /app/
COPY setup_model.sh /app/

RUN setup_model.sh

# Change ownership of the application directory to the non-root user
RUN chown -R myuser:myuser /app

# Switch to the non-root user
USER myuser

# Expose the port that your FastAPI application will run on
EXPOSE 8000

# Command to run your FastAPI application
CMD ["uvicorn", "counter.manage:app", "--host", "0.0.0.0", "--port", "8000"]