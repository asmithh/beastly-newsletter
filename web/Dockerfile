FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN apt-get install -y curl
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN ["chmod", "+x", "docker_entrypoint.sh", "provision_clusters.sh", "wait_for_it.sh"]
ENTRYPOINT ["sh", "./docker_entrypoint.sh"]
CMD ["gunicorn", "-w", "3", "-b", ":5000", "-t", "360", "--reload", "wsgi:app"]
