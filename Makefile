ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
DJANGO_SETTINGS_MODULE ?= 'coppermint.settings'


.PHONY: test_mypy
test_mypy:
	mypy coppermint

.PHONY: test_python
test_python:
	DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
	SESSION_ENGINE=django.contrib.sessions.backends.cache \
	CACHE_URL=locmemcache:// \
	STATICFILES_STORAGE=django.contrib.staticfiles.storage.StaticFilesStorage \
	pytest -vv --capture=sys  --cov=${ROOT_DIR}/coppermint ${ROOT_DIR}/coppermint --cov-report term-missing:skip-covered

.PHONY: test_makemigrations
test_makemigrations:
	DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} python manage.py makemigrations --dry-run --check


.PHONY: test
test: test_mypy test_python  test_makemigrations
