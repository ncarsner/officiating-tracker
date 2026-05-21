FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Node.js for Tailwind CSS build
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Copy project files
COPY . .

# Build Tailwind CSS
RUN npm ci && npm run build

# Collect static files (placeholder env vars satisfy decouple at build time)
RUN SECRET_KEY=build-placeholder \
    API_KEY=build-placeholder \
    DATABASE_URL=sqlite:///tmp/build.db \
    DEFAULT_ADDRESS=build-placeholder \
    ALLOWED_HOSTS=localhost \
    uv run python manage.py collectstatic --noinput

CMD ["uv", "run", "gunicorn", "project.wsgi", "--bind", "0.0.0.0:$PORT", "--log-file", "-"]
