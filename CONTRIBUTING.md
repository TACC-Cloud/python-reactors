# How to contribute

First of all, thank you for taking the time to contribute to this project. We've tried to make a stable project and try to fix bugs and add new features continuously. You can help us do more.

## Getting started

### Check out the roadmap

We have some functionalities in mind and we have issued them and there is a *milestone* label available on the issue. If there is a bug or a feature that is not listed in the **issues** page or there is no one assigned to the issue, feel free to fix/add it! Although it's better to discuss it in the issue or create a new issue for it so there is no confilcting code.

### Writing some code!

Contributing to a project on Github is pretty straight forward. If this is you're first time, these are the steps you should take.

- Fork this repo.

And that's it! Read the code available and change the part you don't like! You're change should not break the existing code and should pass the tests.

If you're adding a new functionality, start from the branch **main**. It would be a better practice to create a new branch and work in there.

When you're done, submit a pull request and for one of the maintainers to check it out. We would let you know if there is any problem or any changes that should be considered.

### Tests

#### GitHub Actions 

GitHub Actions CI will automatically run package tests on pull requests and pushes to `main` branch. Therefore, the recommended method of testing is to simply create a new pull request.

#### Testing Locally

Package-level unit tests are written in pytest and we ask that you run them via [tox][1] in a [poetry][2] virtual environment if running locally. To run all package-level unit tests, which require [tox][1] and [poetry][2] installed and in your `$PATH`, issue: `tox`. Tox will pass positional arguments to pytest, e.g. `tox -- --pdb -xk 'test_can_send_message'`

Note that some tests require a valid [Loggly customer token](https://documentation.solarwinds.com/en/success_center/loggly/content/admin/customer-token-authentication-token.html) set in the environment. The token is already included in the GitHub Secrets for this repository, so these tests will run on Actions CI. To run these tests locally, specify the environment variable when calling `tox`:

```bash
_TEST_LOGGLY_CUSTOMER_TOKEN='f5cc76a7-XXXX-XXXX-XXXX-3864b42c1215' tox
```

If you do not have a valid customer token, simply skip these tests by skipping the tests marked as `loggly_auth`:

```bash
tox -- -k 'not loggly_auth'
```

#### Docker Tests

This repository also maintains a [base Docker image](./Dockerfile) for Tapis Actors. To run unit tests and check CLI usage in the Docker environment, issue:

```bash
# build Docker image and run pytests in the container
make pytest-docker

# check CLI usage within container
make test-cli-docker
```

Note that poetry and Docker are required to run build the image using make. In addition, the user must have a [valid Tapis/Agave credentials cache](https://tapis-cli.readthedocs.io/en/latest/usage/apim.html) at `$HOME/.agave`, since it is used for pytests marked `tapis_auth` and [mounted in the container](https://github.com/TACC-Cloud/python-reactors/blob/97d071416c586d0333a49f5b949580d7f74ff37c/Makefile#L45-L45).

To run all tests mentioned thus far, issue `make tests`.

### Documentation

Every chunk of code that may be hard to understand has some comments above it. If you write some new code or change some part of the existing code in a way that it would not be functional without changing it's usages, it needs to be documented.

## References

Credit to [`mpourismaiel`'s gist](https://gist.github.com/mpourismaiel/6a9eb6c69b5357d8bcc0) for this document's template.

[1]: https://tox.readthedocs.io
[2]: https://python-poetry.org
