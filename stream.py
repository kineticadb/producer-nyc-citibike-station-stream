import os
import sys
import random
import math
import time
import datetime
import json
import copy
import logging

from datetime import timezone
from time import strftime

import requests
from kafka import KafkaProducer

#######################################################################################
# ENVIRONMENT CONFIGS

KAFKA_PASS=os.getenv('KAFKA_SASL_PASS')
KAFKA_USER=os.getenv('KAFKA_SASL_USER')
KAFKA_BRKR=os.getenv('KAFKA_HOST')
KAFKA_PORT=os.getenv('KAFKA_PORT')
KAFKA_TOPIC_STATION_STATUS=os.getenv('KAFKA_TOPIC_STATION_STATUS')
KAFKA_TOPIC_STATION_INFORM=os.getenv('KAFKA_TOPIC_STATION_INFORM')

SRC_URI_STATION_STATUS = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
SRC_URI_STATION_INFORM = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"

REFRESH_DELAY_SECONDS = 30

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARN)

#######################################################################################
# CONNECTIONS

logging.info('Connecting to Kafka')
producer = KafkaProducer(bootstrap_servers=[f"{KAFKA_BRKR}:{KAFKA_PORT}"],
	sasl_plain_username = KAFKA_USER,
	sasl_plain_password = KAFKA_PASS,
	security_protocol="SASL_SSL",
	sasl_mechanism="PLAIN",
	key_serializer=str.encode,
	value_serializer=lambda x:
	json.dumps(x).encode('utf-8'))
logging.info('Connecting to Kafka, completed')

def main():
	

	while True:
		push_stamp = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") #.isoformat()

		try:
			logging.info("Obtaining NYC Citibike Station Satus")
			data_status = requests.get(SRC_URI_STATION_STATUS).json()["data"]["stations"]			
			for ds in data_status:
				#print(ds)
				k = ds["station_id"] if "station_id" in ds else None
				# TODO: only send if the information has changed since the previous bath's data for station key
				producer.send(KAFKA_TOPIC_STATION_STATUS, value=ds, key=k)
			producer.flush()
			print(f"{push_stamp} Pushing status on {len(data_status)} stations")

			logging.info("Obtaining NYC Citibike Station Information")
			data_inform = requests.get(SRC_URI_STATION_INFORM).json()["data"]["stations"]
			for di in data_inform:
				#print(di)
				k = di["station_id"] if "station_id" in di else None
				# TODO: only send if the information has changed since the previous bath's data for station key
				producer.send(KAFKA_TOPIC_STATION_INFORM, value=di, key=k)
			producer.flush()
			print(f"{push_stamp} Pushing information on {len(data_inform)} stations")

		# TODO: keep cache of current batch to check for deltas
			
		except:
			logging.exception("message")

		logging.info(f"Sleeping for {REFRESH_DELAY_SECONDS} seconds until next push")
		time.sleep(REFRESH_DELAY_SECONDS)

		
if __name__ == "__main__":
    main()
