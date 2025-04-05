# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy code and wordbank
COPY grid_hunter.py .
COPY gridhunter_wordbank.json .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default entrypoint to the script
ENTRYPOINT ["python", "grid_hunter.py"]
