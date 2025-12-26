ARG BASE_IMAGE=gpu-base:cuda-12.2.2-ubuntu22.04
FROM ${BASE_IMAGE}

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

RUN cp docker/entrypoint.sh /entrypoint.sh && chmod +x /entrypoint.sh

ARG USER_ID=5000
ARG GROUP_ID=5000
RUN groupadd -g ${GROUP_ID} llm-router && \
    useradd -m -u ${USER_ID} -g llm-router -d /home/llm-router llm-router && \
    chown -R llm-router:llm-router /srv

USER llm-router

RUN mkdir -p /srv/cache && chown llm-router:llm-router /srv/cache
ENV HF_HOME=/srv/cache
#ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/srv/llm-router-services/entrypoint.sh"]