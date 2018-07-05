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

## Run and Check your solution

Here is a simple way how you can get your solution for [Median mission](https://py.checkio.org/en/mission/median/) 

```bash
$ checkio init median checkio_solutions/median.py
```

you have two options here to test your solution. First one is with using `checkio` command

```bash
$ checkio init median checkio_solutions/median.py
```

and the second one is to simply execute the solution

```bash
$ checkio_solutions/median.py
```

## Use multiple domains (py and js)

if you configure Python as default service, you can still use JS. In order to so you need to add key in config sile for `js_checkio` section and then you can run any command with adding extra option `--domain=js` for example

```bash
$ checkio --domain=js sync checkio_solutions
$ checkio --domain=js run median.js
```

## init and test your repository

*TODO*
