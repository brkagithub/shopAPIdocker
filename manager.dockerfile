FROM python:3

RUN mkdir -p /opt/src/shop
RUN mkdir -p /opt/src/shop/manager
WORKDIR /opt/src/shop

COPY applications/shop/configuration.py ./configuration.py
COPY applications/shop/applicationManager.py ./application.py
COPY applications/shop/models.py ./models.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/shop"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "application.py"]
