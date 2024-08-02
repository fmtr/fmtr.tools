export TAG=dev
docker buildx build --file Dockerfile.${TAG} --secret id=HF_TOKEN,env=HF_TOKEN --progress=plain --platform linux/amd64 --load --tag fmtr.tools:${TAG} --build-context tools=../ .