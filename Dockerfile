FROM reg-dev.radlab.dev/ai/gpu-base:cuda-12.2.2-ubuntu22.04

WORKDIR /srv/

RUN mkdir llm-router-services
COPY . /srv/llm-router-services/

WORKDIR /srv/llm-router-services

RUN pip3 install --no-cache-dir .

#RUN pip3 install --no-cache-dir .[api]

COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/srv/llm-router/entrypoint.sh"]
CMD ["--debug"]