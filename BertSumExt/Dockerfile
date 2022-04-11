FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

#set up environment
RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y curl git screen ssh curl
RUN apt-get install unzip
RUN apt-get -y install python3
RUN apt-get -y install python3-pip

WORKDIR /app

RUN cpan install XML::DOM

RUN git clone https://github.com/summanlp/evaluation /app/evaluation && \
export ROUGE=/app/evaluation/ROUGE-RELEASE-1.5.5 && \
cd ${ROUGE}/data/WordNet-2.0-Exceptions/ && \
mv WordNet-2.0.exc.db WordNet-2.0.exc.db.bak && \
./buildExeptionDB.pl . exc WordNet-2.0.exc.db && \
git clone https://github.com/bheinzerling/pyrouge && \
cd pyrouge && pip3 install . && \
pyrouge_set_rouge_path ${ROUGE}

ENV ROUGE=/app/evaluation/ROUGE-RELEASE-1.5.5
ENV CLASSPATH=/app/stanford-corenlp-4.4.0/stanford-corenlp-4.4.0.jar

RUN pip3 install --upgrade pip
RUN pip3 install multiprocess==0.70.9
RUN pip3 install numpy==1.17.2
RUN pip3 install pytorch-transformers==1.2.0
RUN pip3 install tensorboardX==1.9
RUN pip3 install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html

CMD ["/bin/bash"]