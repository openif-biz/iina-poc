# FILE: Dockerfile
# PURPOSE: To build a lightweight container for the IINA PoC Web Frontend.
# DESIGNER: Yuki (Project Owner)
# ENGINEER: Gemini (Chief Engineer)
# ARCHITECTURE: This Dockerfile creates a minimal environment to run the Streamlit reception app,
# without including any heavy AI models or compilation tools.

# Step 1: Base Python Environment
# Use a slim version for a smaller final image size.
FROM python:3.10-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the list of required libraries
# This is done before copying the app code to leverage Docker's layer caching,
# which speeds up future builds if only the app code changes.
COPY requirements.txt .

# Step 4: Install the required libraries
# --no-cache-dir reduces the final image size.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the application source code
COPY . .

# Step 6: Expose the port the container will listen on
# The application inside the container will listen on port 8080.
EXPOSE 8080

# Step 7: Define the command to run when the container starts
# This command starts the Streamlit application.
# --server.port=8080: Explicitly tells Streamlit to use port 8080.
# --server.headless=true: A recommended setting for running in a server environment.
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.headless=true"]
