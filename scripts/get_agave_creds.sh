#!/usr/bin/bash

# Finds JSON-formatted file containing Agave credentials and prints these values
# to STDOUT in a dot env format. Alternatively, use tapis auth show -f json

function die {
    echo ${1} 1>&2
    exit 1
}

# Takes Agave/Tapis credentials file as first argument and attempts to parse
# the file with jq
function readcreds {
    # Check that file exists
    [[ -f ${1} ]] || exit 1
    # Is readable by jq
    cat ${1} | jq -erc . || exit 1
}

# Search for a valid Agave/Tapis credentials file
POSSIBLE_CRED="${HOME}/.agave/current ${HOME}/.tapis/current ${AGAVE_HOME}/current ${TAPIS_HOME}/current"
for file in ${POSSIBLE_CRED}; do
    #echo "Searching for Agave credentials in file ${file}"
    AGAVE_CREDS="$(readcreds ${file})" && break
    #echo "not found in ${file}"
done

if [[ -z ${AGAVE_CREDS} ]]; then
    die "Unable to find Agave credentials file."
fi

# Read API server, username, and access token from credentials
ACCESS_TOKEN="$(echo ${AGAVE_CREDS} | jq -rc .access_token)"
USERNAME="$(echo ${AGAVE_CREDS} | jq -rc .username)"

echo "_abaco_access_token=${ACCESS_TOKEN}"
