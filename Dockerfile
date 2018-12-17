FROM python:3.6.7
ENV PYTHONUNBUFFERED 1

USER root

WORKDIR /code
RUN apt-get update && apt-get install -y ruby ruby-dev && rm -rf /var/lib/apt/lists/*
RUN gem install sass --version 3.5.6
ADD requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install git+git://github.com/kevindice/django-allauth@cb1bfd1

RUN groupadd -r appuser -g 1000 \
    && useradd -u 1000 -r -g appuser -s /bin/false -c "App User" appuser \
    && chmod -R 755 /code

USER appuser
