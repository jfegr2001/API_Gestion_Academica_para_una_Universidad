FROM python:3.12

COPY ./app /app
COPY ./requirements.txt /app
COPY ./startup.sh /app/startup.sh
COPY ./alembic.ini /app
COPY ./alembic /app/alembic

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y mariadb-client && pip install mysqlclient

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x /app/startup.sh

CMD ["/app/startup.sh"]