# 20200831_python_reactors_sdk

## Attendees

* Ethan Ho
* Shweta Gopaulakrishnan

## Agenda

## Development Roadmap

Ethan Ho & Matt Vaughn:
> 1. Separate `reactors` module from `sd2e/base-images`: basically all the devops/testing work required for distribution
> 2. Improve code quality for `Reactor` class
> 3. Restructure code hierarchy such that it is (somewhat) consistent with `tapis-cli` (e.g. usage.py, validate.py, etc. similar to tapis files)
> 4. Build a container-local `reactors` CLI around the above hierarchy
> 5. Update `sd2e/base-images` such that they `pip install tapis-reactors` (or equivalent)
> 6. Integrate the `reactors` CLI with `tapis-cli` : e.g. get `tapis reactors usage --image sd2e/my_reactor` to call `docker sd2e/my_reactor python3 -m reactors usage`
> 7. Work on docs asynchronously throughout this process

## Action Items

* [X] Ethan: quick write-up for Shweta on how to run base-images tests
* [ ] Ethan: work on dev roadmap item #1, which involves porting the SDK source and tests to [TACC-Cloud/python-reactors](https://github.com/TACC-Cloud/python-reactors)
* [ ] Shweta: get acquainted with SD2E/base-images repo, schedule meeting for later this week (week of 8/31)
* [ ] Ethan & Shweta: brainstorm feature requests, from a user standpoint
* [ ] Ethan & Shweta: generate list of questions for Matt, and schedule meeting with him in 1-2 weeks

## Feature Requests

* `agaveutils` module -> custom class that inherits from Agave client
    * Most of these utils take an Agave client as first argument anyway
* Port Ethan's `pipeline_rx_utils` package to `agaveutils`
    * Agave glob function?

## Questions for Matt

* Caveats of reverting to bottom up testing?
    * SDK passes tests for a single (or small subset of) environments
    * Require base images to pass SDK tests for each env
* Currently, running tests for SDK mounts the `~/.agave` directory. Could we loosen this restriction, and only require an `_abaco_access_token` env?
    * I believe one would also need, minimally, a username and API server URL
    * I believe this mimics the production env
* In the Slack thread, you hinted at a discrepancy between an `env.yml` and `usage.yml`; could you expand on this thought a bit?
> So, maybe we don't computationally process an extra file like env.yml - instead maybe we do usage.yml

* What do we think about making this file JSON schema, e.g. `env.jsonschema`?
    * Have the option of [embedding](https://json-schema.org/understanding-json-schema/structuring.html) the `message.jsonschema` in the `message_dict` field of the broader `env.jsonschema`
    * Reactors are already have schema validation methods
    * Would a schema format provide necessary and sufficient information about the required fields in the context?
