FROM nvidia/cuda:9.1-devel-centos7
LABEL maintainer="Trevor Dodds <trevor.dodds@rbccm.com>"
RUN mkdir /scripts/
COPY elasticsearch/gpu_elastic.py /scripts/
CMD python /scripts/gpu_elastic.py
