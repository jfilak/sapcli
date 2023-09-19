# Includes

1. [create](#create)
2. [write](#write)
3. [activate](#activate)
4. [read](#read)

## create

Create executable program

```bash
sapcli include create "ZHELLOWORLD_INC" "Just a description" '$TMP'
```

## write

Change code of an executable program without activation.

```
sapcli include write [OBJECT_NAME|-] [FILE_PATH+|-] [--corrnr TRANSPORT] [--activate] [--ignore-errors] [--warning-errors]
```

* _OBJECT\_NAME_ either include name or - when it should be deduced from FILE\_PATH
* _FILE\_PATH_ if OBJECT\_NAME is not -, single file path or - for reading _stdin_; otherwise space separated list of file paths
* _--corrnr TRANSPORT_ specifies CTS Transport Request Number if needed
* _--activate_ activate after finishing the write operation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## activate

Activate an executable program.

```bash
sapcli include activate [--ignore-errors] [--warning-errors] [--master ZHELLOWORLD] NAME NAME ...
```

* _--master PROGRAM_ sets the master program for include activation
* _--ignore-errors_ continue activating objects ignoring errors
* _--warning-errors_ treat activation warnings as errors

## read

Download source codes

```bash
sapcli include read ZHELLOWORLD_INC
```
