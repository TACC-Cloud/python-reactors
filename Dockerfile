FROM python:3.7-alpine
ARG SDIST
RUN apk update && apk upgrade && apk add git
ADD ${SDIST} /
RUN pip install -q /reactors-*

CMD ["python3", "-m", "reactor.cli", "run"]

# Close out making absolutely sure that work directory is set
WORKDIR ${SCRATCH}
