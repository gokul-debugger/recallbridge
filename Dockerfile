FROM node:22-alpine AS frontend

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html tsconfig*.json vite.config.ts ./
COPY public ./public
COPY src ./src
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    RECALLBRIDGE_AUTO_SYNC=true \
    RECALLBRIDGE_DB=/tmp/recallbridge/recalls.db \
    RECALLBRIDGE_FRONTEND_DIR=/app/dist \
    RECALLBRIDGE_SYNC_INTERVAL=21600

WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN python -m pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY scripts ./scripts
COPY --from=frontend /app/dist ./dist

RUN useradd --create-home --uid 10001 recallbridge \
    && mkdir -p /tmp/recallbridge \
    && chown -R recallbridge:recallbridge /tmp/recallbridge

USER recallbridge
EXPOSE 10000

CMD ["sh", "-c", "python -m uvicorn recallbridge.app:app --host 0.0.0.0 --port ${PORT:-10000}"]
