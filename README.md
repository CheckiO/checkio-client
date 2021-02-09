checkio-client
===================

## About

Command-line tool for playing [**CheckiO games**](https://checkio.org).

[**CheckiO**](https://checkio.org) - Coding games for beginners and advanced programmers where you can improve your coding skills by solving engaging challenges.

## Installation

**python3 is required**

```bash
$ pip3 install --upgrade checkio_client
```

or if you plan to contribute, you can create a clone in a specific folder and install from there

```bash
$ git clone https://github.com/CheckiO/checkio-client.git
...
$ cd checkio-client
$ pip install -e .
```
After the installation a new `checkio` command  becomes available.

## Configuration

your first command should be

```bash
$ checkio config
```

you'll need a key in order to finish it. You can obtain the API Key by following this <a href="https://py.checkio.org/profile/edit/">link</a> for Python, and <a href="https://js.checkio.org/profile/edit/">this one</a> for JavaScript.

You can find all of the available commands by using

```bash
$ checkio -h
```
and the detailed help for a specific command by using (for example, for a `config` command)

```bash
$ checkio config -h
```

The configuration process will create a configuration directory in `$XDG_CONFIG_HOME` or your home folder with a `config.ini` file inside.

```
[Main]
default_domain = py

[py_checkio]
key = b30523506050473b8f33ca440101026a

[js_checkio]

```

## Run and Check your solution

Here is a simple way in which you can get your solution for [Median mission](https://py.checkio.org/en/mission/median/) 

```bash
$ checkio init median checkio_solutions/median.py
```

here you have two options to test your solution. The first one is by using the `checkio` command

```bash
$ checkio check median
```

and the second one is to simply execute the solution with `--check` argument (without it will simply run the solution)

```bash
$ checkio_solutions/median.py --check
```

after the successful check you will get a link for other players’ solutions and a link for sharing your own solution

## Sync all your solutions on one folder

```bash
$ checkio sync ~/checkio_solutions
```

will save all of your solutions in folder `~/checkio_solutions`. Check out help for command sync in order to learn more about the synchronization options

```bash
$ checkio sync -h
```

your last synchronized folder will be saved into `~/.checkio/config.ini`, so if you’ll need to resync your solutions you can simply do

```bash
$ checkio sync
```

and to check and run the solutions by using the simpler command

```bash
$ checkio check median
$ checkio run median
```

## Use multiple domains (py and js)

if you configure Python as a default service, you can still use JS. In order to do so you need to add a key in config file for the `js_checkio` section, and then you can run any command by adding the extra option `--domain=js`, for example,

```bash
$ checkio --domain=js sync checkio_solutions
$ checkio --domain=js run median.js
```

## init and test your repository

**In order to work with repositories module GitPython is required**

by using checkio tools you can also create your own checkio missions

```bash
$ checkio initrepo ~/checkio_mission/new_mission
```

You can link and push the source of your mission into the github repo

```bash
$ checkio linkrepo  ~/checkio_mission/new_mission git@github.com:oduvan/checkio-mission-new-mission.git
```

After you are done editing the mission, you test your mission by using the command

```bash
$ checkio checkrepo ~/checkio_mission/new_mission
```

and open https://py.checkio.org/mission/tester/ in your browser.

To learn more you can check out our [blog post](https://py.checkio.org/blog/cio-task-tester/) on the topic of creating missions on checkio (but with using our old tool) and also [blog post about improving other mission](https://py.checkio.org/blog/how-to-improve-checkio-missions/)
