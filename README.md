# Tapis Actors SDK

This repository contains the software development kit (SDK) for [Tapis Actors](https://tapis.readthedocs.io/en/latest/technical/actors.html).

## Installation

The Actors SDK is installed by default when you initialize a new Actor project using the [Tapis command-line interface (CLI)][3]. This is the recommended usage of this SDK. To initialize a new Actor project using the Tapis CLI, issue:

```bash
tapis actors init
```

Please see the [Tapis CLI documentation][3] for more details.

### Using pip

```bash
pip install git+https://github.com/TACC-Cloud/python-reactors
```

### Build from source

Build wheel and source distribution using [poetry][2]:

```bash
poetry build
```

## Testing

Issue `make tests` to run all tests on Python package and Docker image. Please see the [contribution guide](./CONTRIBUTING.md#tests) for more information on testing.

## Contributing

Thank you for helping improve the Actors SDK! Please see the [contribution guide](./CONTRIBUTING.md) to get started with contributing to the project.

[1]: https://tox.readthedocs.io
[2]: https://python-poetry.org
[3]: https://tapis-cli.readthedocs.io/