FROM radusuciu/readw-dockerized

MAINTAINER Radu Suciu <radusuciu@gmail.com>

USER root

# install some deps
RUN apt-get update && apt-get -y install \
    curl \
    python3-pip \
    python3-venv 


RUN chmod 777 /output
RUN ls -lah /output
RUN /bin/bash -c 'chmod 777 /output'
RUN ls -lah /output

USER wine
WORKDIR /app/flask_readw

ENTRYPOINT ["/bin/bash"]
CMD ["/app/flask_readw/start.sh"]
