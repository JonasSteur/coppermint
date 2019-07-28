FROM python:3.7.4-slim-stretch as base

WORKDIR /app

RUN set -ex \
    # ugly fix to get postgres to install properly
    && mkdir -p /usr/share/man/man1 \
    && mkdir -p /usr/share/man/man7 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        make \
        git \
        gcc \
        python3-dev \
        openssh-client \
        libpq-dev \
        postgresql-contrib \
        postgresql \
        postgresql-client



COPY requirements/requirements.txt /tmp/requirements.txt


RUN set -xe \
    && pip install -U pip \
    && pip install --no-deps --no-cache-dir -r /tmp/requirements.txt

FROM base as dev

COPY . .
COPY requirements/requirements_test.txt /tmp/requirements_test.txt
RUN set -xe \
    && pip install -U pip \
    && pip install --no-deps --no-cache-dir -r /tmp/requirements_test.txt \
    && pre-commit install
RUN python manage.py collectstatic --noinput

EXPOSE 8010

CMD ["python", "manage.py", "runserver", "0.0.0.0:8010"]
