# Use an official Python runtime as a parent image
FROM python:3.11.4-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /buyTech
# install system dependencies
RUN apt-get update && apt-get install -y netcat build-essential libpq-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /buyTech/
RUN pip install -r requirements.txt

# copy project
COPY . /buyTech/
