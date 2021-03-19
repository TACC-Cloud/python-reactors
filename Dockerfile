FROM python:3.7-alpine
ARG SDIST
RUN apk update && apk upgrade && apk add git
ADD ${SDIST} /
RUN pip install -q pytest /reactors-*

# ephemeral working directory
ENV SCRATCH=/mnt/ephemeral-01
WORKDIR ${SCRATCH}
RUN chmod a+rwx ${SCRATCH} && chmod g+rwxs ${SCRATCH}

CMD ["python", "-m", "reactors.cli", "run"]

# ONBUILD
