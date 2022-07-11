FROM python:3

RUN mkdir -p /opt/src/shop
RUN mkdir -p /opt/src/shop/customer
WORKDIR /opt/src/shop

COPY applications/shop/configuration.py ./configuration.py
COPY applications/shop/applicationCustomer.py ./applicationCustomer.py
COPY applications/shop/models.py ./models.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/shop"

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]
ENTRYPOINT ["python", "applicationCustomer.py"]
