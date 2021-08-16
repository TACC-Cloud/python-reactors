"""Get LOGGLY CUSTOMER_TOKEN from Github Secrets and pass it to config.yml"""

import os
import taccconfig
import agavepy
import yaml

def parse_token():
    customer_token = os.environ.get("CUSTOMER_TOKEN_LOGGLY")
    print(customer_token)

    with open('config.yml', 'r') as yamlfile:
        cur_yaml = yaml.safe_load(yamlfile)
        cur_yaml['loggly']['customer_token'] = customer_token

    if cur_yaml:
        with open('config.yml', 'w') as yamlfile:
            yaml.safe_dump(cur_yaml, yamlfile)

    print("parsed")

parse_token()
