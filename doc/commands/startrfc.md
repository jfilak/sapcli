# startrfc

This command allows you to run an arbitrary RFC enabled Function Module.

```bash
sapcli startrfc --output={human,json} RFC_FUNCTION_MODULE {JSON_PARAMETERS,-}
```

* _--output_ allows you to specify format of the output
  * _human_ specifies format which suites human readers
  * _json_ specifies output in JSON

* _RFC\_FUNCION\_MODULE_ name of the executed Function Module

* _JSON\_PARAMETERS_ the call paremeters in the form of JSON object serialized
  into string; if - , then JSON string is read from standard input

## Example: human readable output of STFC\_CONNECTION

Run the function module checking connection to ABAP Trial system deployed in
a docker container.

```bash
sapcli --ashost 172.17.0.2 --sysnr 00 --client 001 --user DEVELOPER --password Down1oad \
       startrfc STFC_CONNECTION '{"REQUTEXT":"ping"}'
```

If everything goes as expected you sould see the following outptu:

```
{'ECHOTEXT': 'ping',
 'RESPTEXT': 'SAP R/3 Rel. 752   Sysid: NPL      Date: 20200223   Time: '
             '231340   Logon_Data: 001/DEVELOPER/E'}
```

## Example: JSON output of RFC\_READ\_TABLE

This example demonstrates JSON format output which we sends through a pipe to
**jq** which then filters out unimportant information.

The example will print out all users of the client 001.


```bash
sapcli --ashost 172.17.0.2 --sysnr 00 --client 001 --user DEVELOPER --password Down1oad \
       startrfc --output=json RFC_READ_TABLE '{"QUERY_TABLE":"USR02","FIELDS":["BNAME"]}' \
  | jq -r ".DATA[].WA" | tr -s ' '
```

If everything goes as expected you should see the following output:

```
BWDEVELOPER
DDIC
DEVELOPER
SAP*
```

## Warning

This command is not available if [PyRFC](https://sap.github.io/PyRFC/index.html)
is not properly installed and you will not even see the parameter in the output
of _sapcli --help_.
