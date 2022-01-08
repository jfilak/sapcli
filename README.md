![Build Status](https://github.com/jfilak/sapcli/actions/workflows/python-package.yml/badge.svg)
[![codecov](https://codecov.io/gh/jfilak/sapcli/branch/master/graph/badge.svg)](https://codecov.io/gh/jfilak/sapcli)

# SAP CLI

Command line interface to SAP products

This tool provides command line interface for ADT which should help you to
build your CI tools.

This tool also provides a limited set of RFC Functionality for the cases
where ADT is no sufficient or possible.

## Installation and usage

First of all you need Python3 (>=3.6) and then you need python-request module.
Nothing else because ADT works on level HTTP.

### Ubuntu

```bash
sudo apt-get install -y git python3 python3-requests python3-openssl python3-venv
git clone https://github.com/jfilak/sapcli.git
cd sapcli
python3 -m venv ve
. ve/bin/activate
pip install -r requirements.txt
./sapcli --help
```

### Enable RFC features

sapcli uses [PyRFC](https://sap.github.io/PyRFC/intro.html) which provides Python API for communication
over SAP NetWeaver RFC.

Please, follow the installation official install instructions at:
[https://sap.github.io/PyRFC/install.html](https://sap.github.io/PyRFC/install.html)

#### Linux hints

It is not necessary to modify */etc/ld.so.conf.d/nwrfcsdk.conf* as you can
just set the environment variable LD\_LIBRARY\_PATH.

The required libraries are compiled the way you can executed them on any x86-64
GNU/Linux, thus you can use the libraries located on your Application server.

## Features

The primary goal was to enable ABAP Unit testing

```bash
sapcli aunit run class zcl_foo --output junit4
sapcli aunit run program zfoo_report --output junit4
sapcli aunit run package '$local_package' --output junit4
```

, ATC checks triggering and installation of [abapGit](https://github.com/larshp/abapGit)
which is delivered as a single source ABAP program (report, SE38 thing).

```bash
sapcli package create '$abapgit' 'git for ABAP by Lars'
sapcli program create 'zabapgit' 'github.com/larshp/abapGit' '$abapgit'
curl https://raw.githubusercontent.com/abapGit/build/master/zabapgit.abap | sapcli program write 'zabapgit' - --activate
```

See the complete list of supported operations in [doc/commands.md](doc/commands.md)

## Usage

You must provide the tool with hostname, client, user and password. It is
possible to use either command line parameters or environment variables.

You can prepare a configuration file like the following:

```bash
cat > .npl001.sapcli.openrc << _EOF
export SAP_USER=DEVELOPER
export SAP_PASSWORD=Down1oad
export SAP_ASHOST=vhcalpnlci
export SAP_CLIENT=001
export SAP_PORT=8000
export SAP_SSL=no
_EOF
```

and the you can source the configuration file in your shell to avoid the need
to repeat the configuration on command line parameters:

```bash
source .npl001.sapcli.openrc

sapcli package create '$abapgit' 'git for ABAP by Lars'
sapcli program create zabapgit 'github.com/larshp/abapGit' '$abapgit'
sapcli aunit run class zabapgit
```

The tool asks only for user and password if missing. All other parameters
either have own default value or causes fatal error if not provided.

Find the complete documentation in [doc/configuration.md](doc/configuration.md)

### RFC usage

When using the RFC features you have to provide the following additional
parameters:

* __--sysnr__ which can be provided as the environment value **SAP\_SYSNR**

## For developers

Your contribution is more than welcome! Nothing is worse than the code that does not exist.

Have a look into [CONTRIBUTING guide](CONTRIBUTING.md), if you are not sure how to start.

And even seasoned GiHub contributors might consider checking out [HACKING guide](HACKING.md).
