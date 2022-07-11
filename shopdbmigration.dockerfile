FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop

COPY applications/shop/migrate.py ./migrate.py
COPY applications/shop/configuration.py ./configuration.py
COPY applications/shop/models.py ./models.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/shop"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "./migrate.py"]
