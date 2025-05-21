FROM python:3.10.15-slim-bookworm

COPY /src/protocol_qc /tmp/protocol_qc/src/protocol_qc
COPY pyproject.toml /tmp/protocol_qc/
RUN python3 -m pip install --upgrade --root-user-action=ignore pip && \
    python3 -m pip install --root-user-action=ignore /tmp/protocol_qc && \
    rm -r /tmp/protocol_qc

ENTRYPOINT ["protocol_qc"]
