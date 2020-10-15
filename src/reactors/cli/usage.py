import yaml
from agavepy.constants import ENV_BASE_URL, ENV_TOKEN
from jinja2 import Environment, PackageLoader, select_autoescape
from reactors.config import config_files, env_vars_from_config, read_config
from reactors.runtime import Reactor
from reactors.validation.jsondoc import load_schema, schema_id, vars_from_schema
from reactors.validation.context import find_context_schema_files
from reactors.validation.message import find_message_schema_files
from .run import docstring, load_function

def usage(args=None):
    env = Environment(
        loader=PackageLoader('reactors.cli', 'templates')
    )
    template = env.get_template('usage.txt.j2')

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
        mdoc = {'file': msf, 'id': msid, 'vars': []}
        msgs.append(mdoc)

    # CONTEXT SCHEMAS
    ctxt_locs = find_context_schema_files()
    ctxts = []
    for csf in ctxt_locs:
        cs = load_schema(csf)
        csid = schema_id(cs)
        csvars = vars_from_schema(cs, filter_private=True)
        cdoc = {'file': csf, 'id': csid, 'vars': csvars}
        ctxts.append(cdoc)

    # CONFIG.YML
    config_locs = config_files()
    union_config_yml = yaml.dump(dict(read_config(namespace=Reactor.CONFIG_NAMESPACE)))
    env_vars = env_vars_from_config(read_config(namespace=Reactor.CONFIG_NAMESPACE), namespace=Reactor.CONFIG_NAMESPACE)
    env_vars.sort()

    print(template.render(docstr=docstr, contexts=ctxts, messages=msgs, config_locs=config_locs, env_vars=env_vars, union_config_yml=union_config_yml, tapis=tapis))
