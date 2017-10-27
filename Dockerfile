FROM python:3.5.2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
EXPOSE 8000/tcp
RUN ["python3", "/code/PracaInzWebApp/manage.py", "makemigrations"]
RUN ["python3", "/code/PracaInzWebApp/manage.py", "migrate"]
ENTRYPOINT ["python3", "/code/PracaInzWebApp/manage.py", "runserver", "0.0.0.0:8000"]