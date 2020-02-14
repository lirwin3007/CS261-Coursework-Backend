![](https://github.com/lirwin3007/CS261-Coursework/workflows/Run%20Lint/badge.svg)
![](https://github.com/lirwin3007/CS261-Coursework/workflows/Run%20Tests/badge.svg)

## Quick Start

To setup a development environment for the Derivatex backend, execute the following:

```shell
~ $ git clone https://github.com/lirwin3007/CS261-Coursework-Backend.git
~ $ cd CS261-Coursework-Backend/
~ $ unzip ~/Downloads/cs261dummydata.zip -d ./res/dummy/
~ $ sudo make init
~ $ sudo make db
```

The dummy data can be downloaded from [here](https://warwick.ac.uk/fac/sci/dcs/teaching/material/cs261/project/cs261dummydata.zip).

Note that the development environment requires a Linux host system, ideally Ubuntu.

## Running

The application can be run in debug mode on a local flask development server using:

```shell
~ $ make run
```

The flask development server can be stopped manually with `Ctrl-C`.

## Testing

Tests can be ran using:

```shell
~ $ make test
```

## Linter

The configured linter tools (pylint, flake8 and bandit) can all be ran using:

```shell
~ $ make test
```

Note that workflows have been setup to execute the linter tools on pull requests into the master and dev branches. Therefore, these tools should be used often locally to ensure these tests pass.


## Cleaning

Clean _Pytest_ and coverage cache/files using:

```shell
~ $ make clean
```
