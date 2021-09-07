"""Get LOGGLY CUSTOMER_TOKEN from Github Secrets and pass it to config.yml"""

import os
import agavepy
import validators
import yaml

def parse_token():
    customer_token = os.environ.get("CUSTOMER_TOKEN_LOGGLY")

    with open('src/reactors/config.yml', 'r') as yamlfile:
        cur_yaml = yaml.safe_load(yamlfile)
        cur_yaml['loggly']['customer_token'] = customer_token

    if cur_yaml:
        with open('src/reactors/config.yml', 'w') as yamlfile:
            yaml.safe_dump(cur_yaml, yamlfile)

    print("parsed")

parse_token()
