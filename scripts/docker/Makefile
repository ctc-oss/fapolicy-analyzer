build:
	sudo podman build --build-arg HTTP_PROXY=${http_proxy} --build-arg HTTPS_PROXY=${https_proxy} -t ctcoss/fapolicy-analyzer -f Dockerfile ../..

run:
	sudo podman run --rm -it --privileged --entrypoint='' ctcoss/fapolicy-analyzer bash
