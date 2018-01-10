BINPATH ?= /usr/bin
GOAPTH ?= go env GOPATH
CONTAINER_DIFF_PATH = $(GOPATH)/src/github.com/GoogleCloudPlatform/container-diff
MERCATOR_GO_PATH = $(GOPATH)/src/github.com/fabric8-analytics/mercator-go

all: container-diff mercator-go


$(GOPATH):
	mkdir -p $(GOPATH)/src


$(BINPATH):
	mkdir -o $(BINPATH)


# We need to build container-diff with gccgo as cgo fails with:
#   user: Current not implemented on linux/amd64 
#
# See https://github.com/golang/go/issues/14625
#
.PHONY: container-diff
container-diff: $(BINPATH)
	[ -d $(CONTAINER_DIFF_PATH) ] \
		|| git clone https://github.com/GoogleCloudPlatform/container-diff $(CONTAINER_DIFF_PATH)
	cd $(CONTAINER_DIFF_PATH) &&\
	  go get -compiler gccgo &&\
	  go build -compiler gccgo -o container-diff &&\
	  cd $(PWD)
	cp $(CONTAINER_DIFF_PATH)/container-diff $(BINPATH)


.PHONY: mercator-go
mercator-go: $(BINPATH)
	[ -d $(MERCATOR_GO_PATH) ] || \
		git clone https://github.com/fabric8-analytics/mercator-go $(MERCATOR_GO_PATH)
	cd $(MERCATOR_GO_PATH) &&\
	  go get &&\
	  make DOTNET=NO RUST=NO JAVA=NO HASKELL=NO build &&\
	  make install &&\
	  cd $(PWD)


.PHONY: pylint
pylint:
	pylint pkgextract.py


.PHONY: clean
clean:
	rm -rf $(BINPATH)
	rm -rf mercator-go/ container-diff/

