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
