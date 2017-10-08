FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements/base_requirements.txt /code/
RUN pip install -r /code/base_requirements.txt
ADD . /code/