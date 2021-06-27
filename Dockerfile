ARG BASE_IMAGE=python:3.7-buster
FROM ${BASE_IMAGE}

# Build args
ARG SCRATCH=/mnt/ephemeral-01
ENV SCRATCH=${SCRATCH}

# Force locale to UTF-8
RUN apt-get update && \
    apt-get install -y locales locales-all && \
    apt-get clean
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# This is a container-local directory that all UIDs can write to. It will
# of course, not survive when the container is torn down.
# Other entries in /mnt/ will be various types of persistent storage
RUN mkdir -p ${SCRATCH} && \
    chmod a+rwx ${SCRATCH} && \
    chmod g+rwxs ${SCRATCH}

# Install Reactors SDK
ADD dist /tmp/reactors-dist
RUN pip install -q /tmp/reactors-dist/*.whl

# Add default Reactor assets
ARG CC_BRANCH=main
ARG CC_DIR=tacc_reactors_base
ARG CC_DEST=/default_actor_context
ARG CC_REPO=https://github.com/TACC-Cloud/cc-tapis-v2-actors.git
RUN python3 -m pip install cookiecutter && \
    cd "$(dirname ${CC_DEST})" && \
    python3 -m cookiecutter --no-input -fc ${CC_BRANCH} --directory ${CC_DIR} \
		${CC_REPO} name=${CC_DEST} alias=${CC_DEST} && \
    # Copy assets to expected dirs
    cp ${CC_DEST}/reactor.py / && \
    cp ${CC_DEST}/config.yml / && \
    # cp ${CC_DEST}/*.jsonschema* / && \
    cp -r ${CC_DEST}/*_schemas / && \
    # Install default pip dependencies
    python3 -m pip install --ignore-installed -r ${CC_DEST}/requirements.txt

# Add Reactor assets on build
ONBUILD ADD requirements.txt /tmp/requirements.txt
ONBUILD RUN python3 -m pip install -r /tmp/requirements.txt
ONBUILD ADD reactor.py /
ONBUILD ADD config.yml /
ONBUILD ADD message.jsonschema context.jsonschema* /

CMD ["python3", "-m", "reactors.cli", "run"]

# Close out making absolutely sure that work directory is set
WORKDIR ${SCRATCH}
