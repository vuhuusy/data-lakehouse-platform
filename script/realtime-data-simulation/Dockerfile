FROM python:3.9-slim

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && mv mc /usr/local/bin/mc && \
    pip install pandas psycopg2-binary

# Copy script & entrypoint
COPY replay.py /app/replay.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /workdir
ENTRYPOINT ["/app/entrypoint.sh"]
