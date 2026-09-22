FROM python:3.13-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install \
    fastapi \
    uvicorn \
    scikit-learn \
    joblib \
    pydantic \
    pydantic-settings \
    && find /install -type d -name "__pycache__" -prune -exec rm -rf {} + \
    && find /install -type d -name "tests" -prune -exec rm -rf {} + \
    && find /install -type d -name "test" -prune -exec rm -rf {} +


FROM python:3.13-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src ./src
COPY models ./models

RUN useradd --create-home appuser

USER appuser

ENV PYTHONPATH=/app/src

EXPOSE 8000

STOPSIGNAL SIGTERM

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/ready')"

CMD ["python", "-m", "uvicorn", "wafi.api.main:app", "--host", "0.0.0.0", "--port", "8000"]