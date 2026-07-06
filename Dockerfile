FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install --default-timeout=300 --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash"]