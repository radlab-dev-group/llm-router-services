FROM gpu-base:cuda-12.2.2-ubuntu22.04

ARG version=prod
ARG GIT_REF=main

LABEL authors="RadLab"
LABEL version=$version

WORKDIR /srv

RUN git clone https://github.com/radlab-dev-group/llm-router-services.git && \
    cd /srv/llm-router-services && \
    git checkout ${GIT_REF}

WORKDIR /srv/llm-router-services

RUN pip3 install --no-cache-dir .

COPY --chmod=0755 entrypoint.sh entrypoint.sh

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/srv/llm-router-services/entrypoint.sh"]