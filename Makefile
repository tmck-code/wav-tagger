build/docker:
	docker build -f Dockerfile -t github.com/tmck-code/wav-tagger:latest .

shell/docker:
	docker run -v $(PWD):/home/wav-tagger -it github.com/tmck-code/wav-tagger:latest bash

.PHONY: build/docker shell/docker
