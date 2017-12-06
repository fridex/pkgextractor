BINPATH = bin


all: container-diff mercator-go


.PHONY: binpath
binpath:
	mkdir -p $(BINPATH)

.PHONY: container-diff
container-diff: binpath
	[ -d container-diff ] || git clone https://github.com/GoogleCloudPlatform/container-diff
	$(MAKE) -C container-diff
	cp container-diff/out/container-diff $(BINPATH)/


.PHONY: mercator-go
mercator-go: binpath
	[ -d mercator-go ] || git clone https://github.com/fabric8-analytics/mercator-go
	$(MAKE) -C mercator-go DOTNET=NO RUST=NO JAVA=NO HASKELL=NO build
	cp mercator-go/mercator $(BINPATH)/mercator
	cp mercator-go/handlers.yml $(BINPATH)/handlers.yml

.PHONY: pylint
pylint:
	pylint pkgextract.py

.PHONY: clean
clean:
	rm -rf $(BINPATH)
	rm -rf mercator-go/ container-diff/

