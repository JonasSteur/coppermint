FROM python:3.7.3-slim-stretch as base

WORKDIR /app

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        make \
        libmariadbclient18 \
        git \
        gcc \
        python3-dev \
        openssh-client \
        libmariadbclient-dev

COPY requirements/requirements.txt /tmp/requirements.txt


RUN set -xe \
    && pip install -U pip \
    && pip install --no-deps --no-cache-dir -r /tmp/requirements.txt

FROM base as dev

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8010

CMD ["python", "manage.py", "runserver", "0.0.0.0:8010"]
