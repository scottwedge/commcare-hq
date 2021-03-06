from django.conf import settings

from corehq.util.io import ClosingContextProxy
from kafka import KafkaConsumer
from kafka.client import KafkaClient, SimpleClient

GENERIC_KAFKA_CLIENT_ID = 'cchq-kafka-client'


def get_simple_kafka_client(client_id=GENERIC_KAFKA_CLIENT_ID):
    # this uses the old SimpleClient because we are using the old SimpleProducer interface
    return ClosingContextProxy(SimpleClient(
        hosts=settings.KAFKA_BROKERS,
        client_id=client_id,
        timeout=30,  # seconds
    ))


def get_kafka_client(client_id=GENERIC_KAFKA_CLIENT_ID):
    return ClosingContextProxy(KafkaClient(
        bootstrap_servers=settings.KAFKA_BROKERS,
        client_id=client_id,
        api_version=settings.KAFKA_API_VERSION
    ))


def get_kafka_consumer():
    return ClosingContextProxy(KafkaConsumer(
        client_id='pillowtop_utils',
        bootstrap_servers=settings.KAFKA_BROKERS,
        request_timeout_ms=1000
    ))
