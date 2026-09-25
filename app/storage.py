import os
from pathlib import Path

import pika

from app.common import CONVERTED_EXCHANGE, connect, declare_topology

def main():
    storage_name = os.getenv("STORAGE_NAME", "storage")
    storage_dir = Path(os.getenv("STORAGE_DIR", f"data/{storage_name}"))
    storage_dir.mkdir(parents=True, exist_ok=True)

    connection = connect()
    channel = connection.channel()
    declare_topology(channel)

    result = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=CONVERTED_EXCHANGE, queue=queue_name)

    def callback(ch, method, properties, body):
        filename = Path((properties.headers or {}).get("filename", "image.bin")).name
        destination = storage_dir / filename
        destination.write_bytes(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[{storage_name}] armazenada: {destination}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(f"[{storage_name}] aguardando imagens convertidas em {storage_dir}...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"[{storage_name}] encerrando")
    finally:
        if connection.is_open:
            connection.close()

if __name__ == "__main__":
    main()
