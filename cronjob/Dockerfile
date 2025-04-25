FROM python:3.10-slim

# Installer cron + procps (pour ps, top, etc.)
RUN apt-get update && apt-get install -y cron procps && apt-get clean

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code backend
COPY backend/app/ .

# Copier le fichier cron (avec la correction)
COPY cronjob/cronjob /etc/cron.d/insert-cron
RUN chmod 0644 /etc/cron.d/insert-cron
RUN crontab /etc/cron.d/insert-cron

RUN apt-get update && apt-get install -y cron procps && apt-get clean

CMD ["bash", "-c", "cron && tail -f /dev/null"]
