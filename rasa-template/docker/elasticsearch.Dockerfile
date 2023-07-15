FROM docker.elastic.co/elasticsearch/elasticsearch:7.17.5

RUN mkdir backup

RUN chown -R elasticsearch:elasticsearch backup
