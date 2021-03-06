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
sapcli atc run {package,class,program} OBJECT_NAME [-r VARIANT] [-e ERROR_LEVEL] [-m MAX_VERDICITS] [-o {human,html,checkstyle}] [-s SEVERITY_MAPPING]
```

* _OBJECT\_NAME_ package, class or program name
* _VARIANT_ if not provided, the system variant from [customizing](#customizing) is used
* _ERROR\_LEVEL_ All ATC Prio numbers higher than this mumber are not considered erros (default: 2)
* _MAX\_VERDICTS_ Total number of verdicts returned (default: 100)
* -o _OUTPUT_ Output format in which checks will be printed (default: human)
* _SEVERITY\_MAPPING_ Severity mapping between ATC PRIO levels and Checkstyle severities (default: None). Could be passed as SEVERITY\_MAPPING env variable. Should be passes as JSON string, example: {"1":"error", "2":"warning", "3":"info"}.

### Output format

#### Human
```
FAKE/TEST/MADE_UP_OBJECT
* 1 :: UNIT_TEST :: Unit tests for ATC module of sapcli
* 2 :: PRIO_2 :: Prio 2
* 3 :: PRIO_3 :: Prio 3
* 4 :: PRIO_4 :: Prio 4
```

#### HTML
```html
<table>
<tr><th>Object type ID</th>
<th>Name</th></tr>
<tr><td>FAKE/TEST</td>
<td>MADE_UP_OBJECT</td></tr>
<tr><th>Priority</th>
<th>Check title</th>
<th>Message title</th></tr>
<tr><td>1</td>
<td>UNIT_TEST</td>
<td>Unit tests for ATC module of sapcli</td></tr>
<tr><td>2</td>
<td>PRIO_2</td>
<td>Prio 2</td></tr>
<tr><td>3</td>
<td>PRIO_3</td>
<td>Prio 3</td></tr>
<tr><td>4</td>
<td>PRIO_4</td>
<td>Prio 4</td></tr>
</table>
```

#### Checkstyle
```xml
<?xml version="1.0" encoding="UTF-8"?>
<checkstyle version="8.36">
<file name="FAKE/TEST&#8725;FOO&#8725;MADE_UP_OBJECT">
<error line="24" column="0" severity="error" message="Unit tests for ATC module of sapcli" source="UNIT_TEST"/>
<error line="32" column="0" severity="error" message="Prio 2" source="PRIO_2"/>
<error line="45" column="0" severity="warning" message="Prio 3" source="PRIO_3"/>
<error line="67" column="0" severity="warning" message="Prio 4" source="PRIO_4"/>
</file>
</checkstyle>
```

##### Severity mapping

By default, sapcli mapps ATC checks to severity the following way:
- PRIO 1 = Error
- PRIO 2 = Error
- PRIO 3 = Warning
- PRIO 4 = Warning
- PRIO 5 = Info

The mapping can be changed via the command line option -s/--severity-mapping
or via the environment variable SEVERITY\_MAPPING. Both options accepts JSON
string encoding an object with 5 properties where names are used for ATC PRIO
numbers (1-5) and values hold Checkstyle severity values - error, warning, info.

The default configuration in JSON is the following:
```json
{"1": "error", "2": "error", "3": "warning", "4": "warning", "5": "info"}
```
