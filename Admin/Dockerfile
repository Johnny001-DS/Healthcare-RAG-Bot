# Use Python 3.11 as the base image
FROM python:3.11

# Expose port 9090 for the Streamlit app
EXPOSE 9090

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files to the container
COPY . ./

# Command to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "admin.py", "--server.port=9090", "--server.address=0.0.0.0"]
