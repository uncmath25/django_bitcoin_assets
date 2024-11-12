FROM python:3.13-slim

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r /requirements.txt

ARG PROJECT_PATH=/django_project
RUN mkdir $PROJECT_PATH
WORKDIR $PROJECT_PATH
# ADD src $PROJECT_PATH

COPY . $PROJECT_PATH

ENTRYPOINT  ["/django_project/entrypoint.sh"]
