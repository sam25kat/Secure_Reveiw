FROM ubuntu:18.04

ENV AWS_ACCESS_KEY_ID=AKIAEXAMPLEFAKE12345
ENV AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
ENV DATABASE_URL=postgres://admin:hunter2@db.internal/prod

RUN apt-get update && apt-get install -y \
    curl \
    sudo \
    openssh-server

ADD https://example.com/installer.sh /tmp/installer.sh
RUN chmod +x /tmp/installer.sh && /tmp/installer.sh

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 22 80 443 8080

CMD ["python", "app.py"]
