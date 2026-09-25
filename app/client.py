import argparse
import json
import os
from pathlib import Path

import pika

from app.common import IMAGES_QUEUE, connect, declare_topology

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def publish_directory(directory: Path, client_name: str):
    connection = connect()
    channel = connection.channel()
    declare_topology(channel)

    files = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED
    )

    if not files:
        print(f"[{client_name}] nenhuma imagem encontrada em {directory}")
        connection.close()
        return

    for path in files:
        body = path.read_bytes()
        headers = {
            "filename": path.name,
            "producer": client_name,
        }
        channel.basic_publish(
            exchange="",
            routing_key=IMAGES_QUEUE,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/octet-stream",
                headers=headers,
            ),
        )
        print(f"[{client_name}] enviada: {path.name} ({len(body)} bytes)")

    connection.close()
    print(f"[{client_name}] envio concluido: {len(files)} imagem(ns)")

def main():
    parser = argparse.ArgumentParser(description="Cliente produtor de imagens")
    parser.add_argument("directory", type=Path, help="Pasta com imagens a enviar")
    args = parser.parse_args()
    if not args.directory.exists() or not args.directory.is_dir():
        raise SystemExit(f"Pasta invalida: {args.directory}")

    client_name = os.getenv("CLIENT_NAME", "client")
    publish_directory(args.directory, client_name)

if __name__ == "__main__":
    main()
