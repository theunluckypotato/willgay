FROM python:3.10-slim

# Install FFmpeg and system audio tools
RUN apt-get update && apt-get install -y ffmpeg gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
