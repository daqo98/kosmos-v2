REPO = quintero98
KVERSCA20_IMAGE = kversca20
KVERSCA20_IMAGE_VERSION = $(KVERSCA20_IMAGE):$(shell git tag --points-at HEAD)

	
release_kversca20:
	
	@if [ -n "$(KVERSCA20_IMAGE_VERSION)" ]; then \
		echo "Building $(KVERSCA20_IMAGE_VERSION)" ;\
		docker build -t $(REPO)/$(KVERSCA20_IMAGE_VERSION) -f Dockerfile_KVerSca20.docker . ;\
		docker push $(REPO)/$(KVERSCA20_IMAGE_VERSION) ;\
	else \
		echo "$(KVERSCA20_IMAGE_VERSION) unchanged: no version tag on HEAD commit" ;\
	fi

release_kversca20_threading:
	
	@if [ -n "$(KVERSCA20_IMAGE_VERSION)" ]; then \
		echo "Building $(KVERSCA20_IMAGE_VERSION)" ;\
		docker build -t $(REPO)/$(KVERSCA20_IMAGE_VERSION) -f Dockerfile_KVerSca20_threading.docker . ;\
		docker push $(REPO)/$(KVERSCA20_IMAGE_VERSION) ;\
	else \
		echo "$(KVERSCA20_IMAGE_VERSION) unchanged: no version tag on HEAD commit" ;\
	fi