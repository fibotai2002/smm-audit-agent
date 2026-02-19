FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies required for Playwright and potential build tools
# We use playwright install --with-deps later, but some basics are good
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Playwright browsers (Chromium only to save space/time)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy project
COPY . /app/

# Create a script to run migrations and start the app
COPY start_bot.sh /start_bot.sh
RUN chmod +x /start_bot.sh

CMD ["/start_bot.sh"]
