FROM python:3
# https://testdriven.io/courses/tdd-fastapi/docker-config/

# Sets the working directory and copies the working directory in
WORKDIR /usr/src
COPY . .

# set environment varibles for python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# All internal ports are 8000
EXPOSE 8000

# install system dependencies
RUN pip install --upgrade pip

# install requirements file
RUN pip install --no-cache-dir -r requirements.txt
