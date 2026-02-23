# Этап, на котором выполняются подготовительные действия
# FROM python:3.11-slim-bullseye as compile
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# RUN python -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"
# COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade pip
#  && pip install --no-cache-dir -r requirements.txt

# Финальный этап
FROM python:3.11-slim-bullseye
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# COPY --from=compile /opt/venv /opt/venv

# ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY app /app/app
COPY ./alembic.ini /app/alembic.ini
COPY ./bash /app/bash
COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable
# RUN uv sync --frozen
RUN chmod a+x /app/bash/*.sh