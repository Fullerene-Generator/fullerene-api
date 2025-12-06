FROM ubuntu:26.04 as builder

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    g++ \
    cmake \
    build-essential \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

COPY external/fullerene-generator/ .

RUN mkdir build && cd build && \
    cmake .. -DCMAKE_CXX_STANDARD=23 && \
    make

FROM python:3.11-slim

COPY --from=builder /build/fullerene_generator /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]