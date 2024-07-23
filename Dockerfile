FROM python:3.11
WORKDIR /graphql-task
COPY . /graphql-task/
RUN rm .env
RUN apt update && apt upgrade
RUN apt install -y build-essential
RUN apt install -y python3-psycopg2
RUN apt install -y postgresql postgresql-contrib 
RUN apt install -y python3-dev libpq-dev
RUN pip3 install -r requirements.txt
RUN export PG_USERNAME=postgres
RUN export PG_PASSWORD=password
RUN export PG_DATABASE=graphql
RUN export PG_HOST=host.docker.internal
ENTRYPOINT ["python3", "-m", "strawberry", "server", "schema"]
