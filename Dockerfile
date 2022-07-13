# pull official base image
FROM python:3.10.5-slim-bullseye
# FROM pypy:3.9-slim-buster https://tonybaloney.github.io/posts/pypy-in-production.html

# RUN apt-get update && apt-get install -y libmagic1

RUN useradd -r -s /bin/bash alex

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

#USER alex
COPY --chown=alex:alex ./migrations /src/migrations
COPY --chown=alex:alex ./alembic.ini /src/alembic.ini
COPY --chown=alex:alex ./app /src/app


WORKDIR /src

# EXPOSE 80

# ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000" "--reload", "--debug"]
CMD uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload --debug --reload-dir /src/app
# ENTRYPOINT ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", ":5000", "app.main:app"]


# EXPOSE 5432