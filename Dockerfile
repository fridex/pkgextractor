FROM fedora:27

ENV LANG=en_US.UTF-8 \
    PKGEXTRACTOR_TMP_DIR='/tmp/pkgextractor' \
    GOPATH='/tmp/go'
ENTRYPOINT ["pkgextract"]

RUN dnf update -y &&\
  dnf install -y python3-pip python-pip findutils atomic go gcc-go git make docker # findutils needed for xargs

# Install pkgextract itself
RUN mkdir -p ${PKGEXTRACTOR_TMP_DIR}
COPY . ${PKGEXTRACTOR_TMP_DIR}
RUN cd ${PKGEXTRACTOR_TMP_DIR} &&\
  make &&\
  pip3 install .
RUN unset PKGEXTRACTOR_TMP_DIR

CMD ["pkgextract"]
