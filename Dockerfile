# PULL THE BASE IMAGE
FROM python:3.10.12-slim-bookworm

## SET ENVIRONMENT VARIABLES
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
# INSTALL DEPENDENCIES
RUN pip install -r requirements.txt

# COPY PROJECT
COPY . .

# RUN SERVER (migrations will run at container startup)
CMD python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000