import io
import os

import pika
from PIL import Image

from app.common import CONVERTED_EXCHANGE, IMAGES_QUEUE, connect, declare_topology

def to_grayscale(image_bytes: bytes) -> bytes:
    with Image.open(io.BytesIO(image_bytes)) as image:
        original_format = image.format or "PNG"
        gray = image.convert("L")
        output = io.BytesIO()
        save_format = "JPEG" if original_format.upper() in {"JPG", "JPEG"} else original_format
        gray.save(output, format=save_format)
        return output.getvalue()

def main():
    worker_name = os.getenv("CONVERTER_NAME", "converter")
    connection = connect()
    channel = connection.channel()
    declare_topology(channel)

    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        filename = (properties.headers or {}).get("filename", "image.bin")
        producer = (properties.headers or {}).get("producer", "unknown")
        try:
            converted = to_grayscale(body)
            ch.basic_publish(
                exchange=CONVERTED_EXCHANGE,
                routing_key="",
                body=converted,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                    content_type="application/octet-stream",
                    headers={
                        "filename": filename,
                        "producer": producer,
                        "converter": worker_name,
                    },
                ),
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[{worker_name}] convertida: {filename} -> publicada para armazenamento")
        except Exception as exc:
            print(f"[{worker_name}] erro ao converter {filename}: {exc}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=IMAGES_QUEUE, on_message_callback=callback)
    print(f"[{worker_name}] aguardando imagens...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"[{worker_name}] encerrando")
    finally:
        if connection.is_open:
            connection.close()

if __name__ == "__main__":
    main()
