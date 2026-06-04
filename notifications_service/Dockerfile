FROM python:3.11-slim

WORKDIR /app

COPY notifications_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY broker/ ./broker/
COPY event_contracts ./event_contracts/
COPY infrastructure ./infrastructure/
COPY notifications_service ./notifications_service/

ENV PYTHONPATH=/app

CMD [ "python", "-m", "notifications_service.main" ]
