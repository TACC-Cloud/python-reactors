import json
import yaml
from agavepy.constants import ENV_BASE_URL, ENV_TOKEN
from jinja2 import Environment, PackageLoader, select_autoescape
from reactors.config import config_files, env_vars_from_config, read_config
from reactors.runtime import Reactor
from reactors.validation.context import find_context_schema_files
from reactors.validation.jsondoc import (load_schema, schema_id,
                                         vars_from_schema)
from reactors.validation.message import find_message_schema_files

from .run import docstring, load_function

# TODO
# DEBUG
# ex_msg is not defined
ex_msg = str()


def usage(args=None):
    env = Environment(loader=PackageLoader('reactors.cli', 'templates'))
    template = env.get_template('usage.txt.j2')

    image_repo = '<NAMESPACE/REPO:TAG>'

    # Function DOCSTRING
    try:
        docstr = docstring(load_function())
    except Exception:
        docstr = 'Unknown'

    # TAPIS details
    tapis = {'api_server': ENV_BASE_URL, 'api_token': ENV_TOKEN}

    # MESSAGE SCHEMAS
    msgsch_locs = find_message_schema_files()
    msgs = []
    for msf in msgsch_locs:
        ms = load_schema(msf)
        msid = schema_id(ms)
        msx = '{}'
        mdoc = {'file': msf, 'id': msid, 'vars': [], 'schema': ms}
        msgs.append(mdoc)

    # Example message
    if len(msgs) <= 2:
        ms = msgs[0]['schema']
        ex_sch = json.dumps(ms, indent=2)
    else:
        ex_sch = None

    # Env Var Sets
    ctxt_locs = find_context_schema_files()
    ctxts = []
    for csf in ctxt_locs:
        cs = load_schema(csf)
        csid = schema_id(cs)
        csvars = vars_from_schema(cs, filter_private=True)
        cdoc = {'file': csf, 'id': csid, 'vars': csvars, 'schema': cs}
        ctxts.append(cdoc)

    # Env Vars
    # We compute and display this if the number of
    # contexts is limited to 2 or less, which implies
    # the default (which cannot be overridden) and one more
    if len(ctxts) <= 2:
        req_vars = []
        cli_envs = []
        cli_envs_str = ''
        for c in ctxts:
            for v in c['vars']:
                if True:
                    #if v['required']:
                    req_vars.append(v)
                    val = v.get('default', None)
                    if val is None:
                        if len(v.get('examples', [])) > 0:
                            val = v.get('examples')[0]
                        else:
                            val = '<{0}>'.format(v.get('type', 'str'))
                    # Exception for MSG = it should be the example message from above not <str>
                    if v.get('id') != 'MSG':
                        cli_envs.append('{0}="{1}"'.format(v.get('id'), val))
                    else:
                        cli_envs.append(
                            'MSG=\'{0}\''.format(ex_msg))
        cli_envs_str = ' '.join(cli_envs)
    else:
        req_vars = None
        cli_envs = None
        cli_envs_str = None

    # CONFIG.YML
    config_locs = config_files()
    union_config_yml = yaml.dump(
        dict(read_config(namespace=Reactor.CONFIG_NAMESPACE)))
    config_vars = env_vars_from_config(
        read_config(namespace=Reactor.CONFIG_NAMESPACE),
        namespace=Reactor.CONFIG_NAMESPACE)
    config_vars.sort()

    print(
        template.render(docstr=docstr,
                        contexts=ctxts,
                        messages=msgs,
                        config_locs=config_locs,
                        config_vars=config_vars,
                        union_config_yml=union_config_yml,
                        tapis=tapis,
                        req_vars=req_vars,
                        ex_sch=ex_sch,
                        cli_envs_str=cli_envs_str,
                        image_repo=image_repo))
