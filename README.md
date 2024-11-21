<div align="center">

# `bagel-cli`
[![codecov](https://codecov.io/gh/neurobagel/bagel-cli/graph/badge.svg?token=R1KI9KIP8D)](https://codecov.io/gh/neurobagel/bagel-cli)
[![Tests](https://github.com/neurobagel/bagel-cli/actions/workflows/test.yml/badge.svg)](https://github.com/neurobagel/bagel-cli/actions/workflows/test.yml)
[![Docker Image Version](https://img.shields.io/docker/v/neurobagel/bagelcli?label=docker)](https://hub.docker.com/r/neurobagel/bagelcli/tags)
[![Python versions](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=flat)](https://www.python.org)
[![License](https://img.shields.io/github/license/neurobagel/bagel-cli?color=CD5C5C&style=flat)](LICENSE)

</div>

The `bagel-cli` is a Python command-line tool to automatically parse and describe subject phenotypic and imaging attributes in an annotated dataset for integration into the Neurobagel graph.

**Please refer to our [official Neurobagel documentation](https://neurobagel.org/user_guide/cli/) for information on how to install and use the CLI.**


## Development environment

To ensure that our Docker images are built in a predictable way,
we use `requirements.txt` as a lock-file.
That is, `requirements.txt` includes the entire dependency tree of our tool,
with pinned versions for every dependency (see [here](https://pip.pypa.io/en/latest/topics/repeatable-installs/#repeatability) for more information).


### Setting up a local development environment
To work on the CLI, we suggest that you create a development environment 
that is as close as possible to the environment we run in production.

1. Install the dependencies from the lockfile (`dev_requirements.txt`):

    ```bash
    pip install -r dev_requirements.txt
    ```

2. Install the CLI without touching the dependencies:

    ```bash
    pip install --no-deps -e .
    ```

3. Install the `bids-examples` and `neurobagel_examples` submodules needed to run the test suite:
    ```bash
    git submodule init
    git submodule update
    ```

Confirm that everything works well by running the tests: 
`pytest .`

### Setting up code formatting and linting (recommended)

[pre-commit](https://pre-commit.com/) is configured in the development environment for this repository, and can be set up to automatically run a number of code linters and formatters on any commit you make according to the consistent code style set for this project.

Run the following from the repository root to install the configured pre-commit "hooks" for your local clone of the repo:
```bash
pre-commit install
```

pre-commit will now run automatically whenever you run `git commit`.

### Updating Python lock-file
The `requirements.txt` file is automatically generated from the `setup.cfg`
constraints. To update it, we use `pip-compile` from the `pip-tools` package.
Here is how you can use these tools to update the `requirements.txt` file.

_Note: `pip-compile` will update dependencies based on the Python version of the environment it's running in._

1. Ensure `pip-tools` is installed:
    ```bash
    pip install pip-tools
    ```
2. Update the runtime dependencies in `requirements.txt`:
    ```bash
    pip-compile -o requirements.txt --upgrade
    ```
3. The above command only updates the runtime dependencies.
Now, update the developer dependencies in `dev_requirements.txt`:
    ```bash
    pip-compile -o dev_requirements.txt --extra all --upgrade
    ```

## Regenerating the Neurobagel vocabulary file
Terms in the Neurobagel namespace (`nb` prefix) and their class relationships are serialized to a file 
called [nb_vocab.ttl](https://github.com/neurobagel/recipes/blob/main/vocab/nb_vocab.ttl), which is automatically
uploaded to new Neurobagel graph deployments.
This vocabulary is used by Neurobagel APIs to fetch available attributes and attribute instances from a graph store.

When the Neurobagel graph data model is updated (e.g., if new classes or subclasses are created), 
this file should be regenerated by running:
```bash
python generate_nb_vocab_file.py
```
This will create a file called `nb_vocab.ttl` in the current working directory.
