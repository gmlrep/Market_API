# Этап, на котором выполняются подготовительные действия
FROM python:3.11-slim-bullseye as compile
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Финальный этап
FROM python:3.11-slim-bullseye
COPY --from=compile /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY app /app/app
COPY ./alembic.ini /app/alembic.ini
COPY ./bash /app/bash
RUN chmod a+x /app/bash/*.sh