FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git build-essential \
    && rm -rf /var/lib/apt/lists/*

ARG ASTROLOGY_DATABASE_REPO=https://github.com/alexmarroig/Astrologydatabase.git
ARG ASTROLOGY_DATABASE_REF=main

RUN git clone --depth 1 --branch "${ASTROLOGY_DATABASE_REF}" "${ASTROLOGY_DATABASE_REPO}" .

RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    DEBUG=false \
    EPHEMERIS_PROVIDER=analytical

EXPOSE 8000

CMD ["/start.sh"]
