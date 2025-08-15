FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt

# Copy your project code into the image
COPY . /app

# Expose whatever port your server uses (example: 5555)
EXPOSE 5555

# Run as a module (note: no .py at end)
CMD ["python", "-m", "src.engine.server_side"]
