FROM python:3.6-slim

LABEL maintainer="support@kinetica.com"
LABEL Description="Kinetica Machine Learning 'Bring Your Own Container' Sample Continuous Ingestor: NYC CitiBike Station Status and Bike Inventory"
LABEL Author="Saif Ahmed"

RUN mkdir /opt/gpudb
RUN mkdir /opt/gpudb/kml
RUN mkdir /opt/gpudb/kml/slipway
WORKDIR /opt/gpudb/kml/slipway

COPY requirements.txt ./

RUN pip install -r requirements.txt --no-cache-dir

COPY stream.py ./
COPY runner.sh ./

CMD ["/opt/gpudb/kml/slipway/runner.sh"]
