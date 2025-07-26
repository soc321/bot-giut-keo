# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Start the bot
CMD ["python", "bot.py"]
