import datetime
import os
import sys
import threading
from json import loads

from kafka import KafkaConsumer

import config.global_temp_config as config

received_messages = []
consumer = None
kafka_handler = None
server = config.kafka_endpoint
topic = config.kafka_topic
stop = False


def init_kafka():
    global consumer
    global kafka_handler
    global received_messages
    global stop
    stop = False
    if consumer is None:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[server],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='my-group' + os.getenv('PYTEST_XDIST_WORKER', ''),  # fix groups for parallel kafka
            value_deserializer=lambda x: loads(x.decode('utf-8')))
    received_messages = []
    kafka_handler = threading.Thread(target=kafka_handler_f, args=())
    kafka_handler.start()
    print("init kafka")
    print(f"kafka param = {'my-group' + os.getenv('PYTEST_XDIST_WORKER', '')}")


def finalize_kafka():
    global consumer
    global kafka_handler
    global stop
    stop = True
    kafka_handler.join()
    consumer.close()
    consumer = None
    print("finalize kafka")


def kafka_handler_f():
    global consumer
    global received_messages
    while not stop:
        try:
            raw_message = consumer.poll(1000, 10)
            partitions = [raw_message[x] for x in raw_message.keys()]
            for arr in partitions:
                for message in arr:
                    received_messages.append(message)
        except Exception as e:
            print(e, file=sys.stderr)
            pass
    print("end kafka handler")


def find_all_messages_by_number(msisdn, datefrom):
    result = []
    for message in received_messages:
        msg_value = message.value
        if 'event_time' not in msg_value:
            continue

        event_date = datetime.datetime.strptime(msg_value['event_time'], "%Y-%m-%dT%H:%M:%SZ")

        if 'msisdn' in msg_value and msg_value['msisdn'] == msisdn and event_date > datefrom:
            result.append(msg_value)

    return result
