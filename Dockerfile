FROM klee/klee:latest

USER root

WORKDIR /klee-test-gen

RUN apt-get update                                  \
    && apt-get install -y --no-install-recommends   \
        python3=3.*                                 \
        python3-pip                                 \
        git                                         \
    && apt-get clean                                \
    && rm -rd /var/lib/apt/lists/*

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . /klee-test-gen

VOLUME [ "/klee-test-gen/vectors" ]

ENTRYPOINT [ "/usr/bin/python3" ]
CMD [ "main.py", "--max-functions", "1500" ]
