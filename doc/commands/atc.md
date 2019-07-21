# ATC

1. [customizing](#customizing)
1. [run](#run)

## customizing

Fetches and prints out ATC configuration.

```bash
sapcli atc customizing
```

## run

Executes ATC Checks on the given object and exits with non-zero code,
if ATC findings of Prio higher then the configured level are found.

```bash
sapcli atc run {package,class,program} OBJECT_NAME [-r VARIANT] [-e ERROR_LEVEL] [-m MAX_VERDICITS]
```

* _OBJECT\_NAME_ package, class or program name
* _VARIANT_ if not provided, the system variant from [customizing](#customizing) is used
* _ERROR\_LEVEL_ All ATC Prio numbers higher than this mumber are not considered erros (default: 2)
* _MAX\_VERDICTS_ Total number of verdicts returned (default: 100)

