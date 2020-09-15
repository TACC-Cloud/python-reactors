FROM sd2e/python3:ubuntu17

# Force locale to UTF-8
RUN apt-get update && \
    apt-get install -y locales locales-all && \
    apt-get clean
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

ARG CHANNEL=edge
ARG LANGUAGE=python3
ARG VERSION=0.8.1
ARG SDIST
ARG SDK_HOME=/reactors
ARG SCRATCH=/mnt/ephemeral-01
ARG AGAVEPY_BRANCH=master
ARG DATACATALOG_BRANCH=v2.0.0

# TODO: redundant. Same info is given in the sdist/PKG-INFO
# Discoverable version inside the container
RUN echo "TACC.cloud Reactors\nLanguage: ${LANGUAGE}\nVersion: ${VERSION}" > /etc/reactors-VERSION

# Helpful env variable
ENV REACTORS_VERSION=${VERSION}
ENV SCRATCH=${SCRATCH}

# This is a container-local directory that all UIDs can write to. It will
# of course, not survive when the container is torn down.
# Other entries in /mnt/ will be various types of persistent storage
RUN mkdir -p ${SCRATCH} && \
    chmod a+rwx ${SCRATCH} && \
    chmod g+rwxs ${SCRATCH}
ENV _REACTOR_TEMP=${SCRATCH}

# Install components from Python SDK, which is still maintained in the
# base-images repo, but is being prepared to move to a standalone repository

# The main client-side SDK. Adds extended capability and utility functions
# to the Python runtime.
ADD ${SDIST} /
RUN pip install -q /reactors-*

# Track to latest SD2 datacatalog
# RUN pip3 install --upgrade git+https://github.com/SD2E/python-datacatalog.git@${DATACATALOG_BRANCH}

# JSONschema 3.x RC
# RUN pip3 install --upgrade git+git://github.com/Julian/jsonschema@v3.0.0a3#egg=jsonschema

CMD ['/bin/bash']

# Close out making absolutely sure that work directory is set
WORKDIR ${SCRATCH}
