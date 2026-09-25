import os
import time
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
IMAGES_QUEUE = "images.to_convert"
CONVERTED_EXCHANGE = "images.converted"

def connect(max_attempts: int = 30):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=60,
                    blocked_connection_timeout=120,
                )
            )
            return connection
        except pika.exceptions.AMQPConnectionError as exc:
            last_error = exc
            print(f"[RabbitMQ] tentativa {attempt}/{max_attempts} falhou; aguardando...")
            time.sleep(2)
    raise RuntimeError(f"Nao foi possivel conectar ao RabbitMQ em {RABBITMQ_HOST}") from last_error

def declare_topology(channel):
    channel.queue_declare(queue=IMAGES_QUEUE, durable=True)
    channel.exchange_declare(
        exchange=CONVERTED_EXCHANGE,
        exchange_type="fanout",
        durable=True,
    )
