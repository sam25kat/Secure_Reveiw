FROM python:3.7-buster

ENV STRIPE_API_KEY=sk_test_EXAMPLE_FAKE_KEY_FOR_TESTING
ENV DJANGO_SECRET_KEY=django-insecure-hardcoded-prod-secret
ENV DEBUG=True

RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    curl

ADD https://example.com/installer.sh /tmp/installer.sh
RUN chmod +x /tmp/installer.sh && /tmp/installer.sh

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app/
WORKDIR /app

EXPOSE 22
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
