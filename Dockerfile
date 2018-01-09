FROM centos:7

ENV LANG=en_US.UTF-8 \
    PKGEXTRACTOR_TMP_DIR='/tmp/pkgextractor' \
    GOPATH='/tmp/go'
ENTRYPOINT ["pkgextract"]

RUN yum install -y epel-release &&\
  yum update -y &&\
  yum install -y python34-pip python-pip findutils go git make docker &&\
  yum clean all

# Install pkgextract itself
RUN mkdir -p ${PKGEXTRACTOR_TMP_DIR}
COPY . ${PKGEXTRACTOR_TMP_DIR}
RUN cd ${PKGEXTRACTOR_TMP_DIR} &&\
  make &&\
  pip3 install .
RUN unset PKGEXTRACTOR_TMP_DIR

CMD ["pkgextract"]
