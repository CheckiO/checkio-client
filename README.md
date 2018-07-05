checkio-client
===================

## Installation

**python3 is required**

```bash
$ pip install --force-reinstall git+https://github.com/CheckiO/checkio-client.git
```

or, if you plan to contribute you can make a clone into specific folder and then install from there

```bash
$ git clone https://github.com/CheckiO/checkio-client.git
...
$ cd checkio-client
$ pip install -e .
```
After installation new command `checkio` become available.

## Configuration

in your first run you should do

```bash
$ checkio config
```

you will need a key in order to finsh it. How to get the key will be shown during installation.

You can find all available commands using

```bash
$ checkio -h
```
and detailed help for specific command using (for example for command `config`)

```bash
$ checkio config -h
```

The configuration process will create a `.checkio` in your home folder and with one file `config.ini` in it

```
[Main]
default_domain = py

[py_checkio]
key = b30523506050473b8f33ca440101026a

[js_checkio]

```

## Sync with folder



## Use multiple domains (py and js)

*TODO*

## init and test your repository

*TODO*
