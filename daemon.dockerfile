FROM python:3

RUN mkdir -p /opt/src/shop
RUN mkdir -p /opt/src/shop/daemon
WORKDIR /opt/src/shop

COPY applications/shop/configuration.py ./configuration.py
COPY applications/shop/daemon.py ./daemon.py
COPY applications/shop/models.py ./models.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/shop/daemon"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "daemon.py"]
