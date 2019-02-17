# SAP CLI [![Build Status](https://travis-ci.org/jfilak/sapcli.svg?branch=master)](https://travis-ci.org/jfilak/sapcli)

Command line interface to SAP products

This tool provides command line interface for ADT which should help you to
build your CI tools.

## Installation and usage

First of all you need Python3 (>=3.6) and then you need python-request module.
Nothing else because ADT works on level HTTP.

### Ubuntu

```bash
sudo apt-get install git python3 python3-requests python3-openssl

git clone https://github.com/jfilak/sapcli.git
cd sapcli

export PYTHONPATH=$(pwd):$PYTHONPATH

bin/sapcli --help
```

## Features

The primary goal was to enable ABAP Unit testing

```bash
sapcli --ahost ... --client ... aunit run class zcl_foo
sapcli --ahost ... --client ... aunit run program zfoo_report
sapcli --ahost ... --client ... aunit run package '$local_package'
```

, ATC checks triggering and installation of [abapGit](https://github.com/larshp/abapGit)
which is delivered as a single source ABAP program (report, SE38 thing).

```bash
sapcli --ashost ... --client ... package create '$abapgit' 'git for ABAP by Lars'
sapcli --ashost ... --client ... program create 'zabapgit' 'github.com/larshp/abapGit' '$abapgit'
curl https://raw.githubusercontent.com/abapGit/build/master/zabapgit.abap | sapcli --ashost ... --client ... program write 'zabapgit' -
sapcli --ashost ... --client ... program activate 'zabapgit'
```

See the complete list of supported operations in [doc/commands.md](doc/commands.md)
