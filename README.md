# Atividade 01 U1 - Sistemas Distribuidos - RabbitMQ

Implementacao da atividade da disciplina COMP0470 (Sistemas Distribuidos) usando RabbitMQ e Docker.

## Arquitetura

```text
clientes/produtores
 client1 ----\
              > [fila images.to_convert] --> converter1 --\
 client2 ----/                              converter2 ----> [fanout images.converted]
                                                               |              |
                                                               v              v
                                                           storage1       storage2
```

- Os **clientes** enviam imagens para uma unica fila.
- Os **conversores** sao consumidores concorrentes da mesma fila. Cada imagem e processada por apenas um conversor.
- O conversor transforma a imagem para **escala de cinza**.
- Depois da conversao, a imagem e publicada em um **exchange fanout**.
- Cada servidor de armazenamento possui sua propria fila temporaria ligada ao exchange, entao **todos os storages recebem todas as imagens**.
- O nome original do arquivo e transportado nos headers da mensagem e preservado no salvamento.

## Requisitos

- Docker
- Docker Compose

## Executar

### 1. Gerar imagens de teste

```bash
docker compose run --rm converter1 python scripts/generate_samples.py
```

Como o comando acima executa dentro do container sem montar as pastas dos clientes, a forma mais simples para testes locais e gerar usando Python local:

```bash
python -m pip install -r requirements.txt
python scripts/generate_samples.py
```

Ou coloque manualmente imagens em:

```text
data/client1/
data/client2/
```

### 2. Subir RabbitMQ, conversores e servidores de armazenamento

```bash
docker compose up --build rabbitmq converter1 converter2 storage1 storage2
```

Em outro terminal, envie as imagens dos dois clientes:

```bash
docker compose --profile clients run --rm client1
docker compose --profile clients run --rm client2
```

Tambem e possivel subir todos os clientes do profile de uma vez:

```bash
docker compose --profile clients up --build
```

> Nesse modo os clientes enviam o conteudo das pastas e terminam. Os consumidores continuam executando.

### 3. Conferir o resultado

Apos o processamento, confira:

```text
data/storage1/
data/storage2/
```

Os dois diretorios devem conter as mesmas imagens convertidas para tons de cinza, mantendo os nomes originais.

## RabbitMQ Management

Com os containers em execucao:

- http://localhost:15672
- usuario: `guest`
- senha: `guest`

## Teste de escalabilidade

O Compose sobe dois conversores. Para testar mais consumidores:

```bash
docker compose up --build --scale converter1=3 converter2 storage1 storage2
```

Voce tambem pode abrir varios clientes em terminais diferentes para publicar simultaneamente.

## Conceitos demonstrados

- RabbitMQ / AMQP
- Producer e Consumer
- Queue
- Competing Consumers
- Exchange `fanout`
- Publish/Subscribe
- ACK/NACK
- `basic_qos(prefetch_count=1)`
- Mensagens persistentes
- Docker e Docker Compose
- Processamento distribuido e redundancia de armazenamento
