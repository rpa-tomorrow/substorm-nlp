# RPA Tomorrow - process tasks from natural text

The purpose of RPA Tomorrow is to implement a system where the user can write instructions in clear text in order to instruct the computer what to do. This application utilizes natural language processing together with custom-made neural networks in order to parse the intent of the given text and then returns an executable task.

For users of the system there are two user interfaces implemented, a CLI and a GUI.

[![asciicast](https://asciinema.org/a/NJHkkxjK2dXprr2pV6fb2DXgL.svg)](https://asciinema.org/a/NJHkkxjK2dXprr2pV6fb2DXgL)

## Table of contents
1. [Requirements](#requirements)
2. [Setup](#setup)
    1. [Advanced setup](#advanced-setup)
3. [Quickstart](#quickstart)
4. [Usage](#usage)
    1. [CLI](#cli)
    2. [GUI](#gui)
5. [Documentation](#documentation)
6. [Testing](#testing)
7. [License](#license)

## Requirements

Linux and Windows:
- Python 3+
- Anaconda or Miniconda

Windows Only:
- Microsoft C++ Build Tools (for GUI)

## Quickstart

1. Follow the [setup](#setup)
2. Start the application through either the [CLI](#cli) or [GUI](#gui)

## Setup

Clone and `cd` into the repository.

To create and activate the project environment the included setup script can be used 
```bash
$ source substorm.sh
```

Otherwise you can do it manually
```bash
# Create environment
$ conda env create -f substorm-nlp.yml
# Install RPA models
$ pip install -r requirements.txt
# Activate environment
$ conda activate substorm-nlp
```
**NOTE!** If you're on Windows, replace all `substorm-nlp` with `substorm-nlp-win` above.

### Advanced setup
- To authenticate with Google for GCal support see [google_auth_setup.md](docs/google_auth_setup.md)
- User settings can be configured manually inside `config/` or through the GUI

## Usage


See [accepted_input.md](docs/accepted_input.md) if the program is struggling to understand the input.

### CLI

The CLI can be started as follows
```bash
$ python lib/cli/cli.py
```
Inside the CLI, type `help` for more instructions. 

### GUI

The GUI can be started as follows
```bash
$ fbs run
```

## Documentation

Documentation are provided in `docs/`.


## Testing

The tests can be run with the following command

```bash
$ pytest
```
A coverage report will automatically be generated and saved in `htmlcov/` and it can be viewed at `htmlcov/index.html`

## License

Licensed under the MIT license. See [LICENSE](LICENSE) for details.
