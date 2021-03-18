FROM python:3.7-alpine
ARG SDIST
RUN apk update && apk upgrade && apk add git
ADD ${SDIST} /
RUN pip install -q pytest /reactors-*

