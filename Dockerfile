FROM node:22-slim AS assets
WORKDIR /app/build
COPY build/package.json build/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY build/ ./
RUN yarn build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
WORKDIR /app

# docker-compose passes requirements-dev.txt so the dev stack can run the tests.
ARG REQUIREMENTS=requirements.txt
COPY requirements.txt requirements-dev.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-libmysqlclient-dev gcc pkg-config \
    && pip install --no-cache-dir -r $REQUIREMENTS \
    && apt-get purge -y gcc pkg-config && apt-get autoremove -y \
    && apt-get install -y --no-install-recommends libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

COPY . .
COPY --from=assets /app/static/dist ./static/dist
RUN rm -rf build tests docs spec \
    && DJANGO_SECRET_KEY=build ALLOWED_HOSTS=build python manage.py collectstatic --noinput \
    && mkdir -p /app/data/media && chmod +x entrypoint.sh

EXPOSE 8000
VOLUME /app/data
ENTRYPOINT ["./entrypoint.sh"]
CMD ["sh", "-c", "exec gunicorn vergissmeinnicht.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-1} --access-logfile - --error-logfile -"]
