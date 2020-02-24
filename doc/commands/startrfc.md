# startrfc

This command allows you to run an arbitrary RFC enabled Function Module.

```bash
sapcli startrfc RFC_FUNCTION_MODULE {JSON_PARAMETERS,-}
```

* _RFC\_FUNCION\_MODULE_ name of the executed Function Module

* _JSON\_PARAMETERS_ the call paremeters in the form of JSON object serialized
  into string; if - , then JSON string is read from standard input

## Examples

Run the function module checking connection to ABAP Trial system deployed in
a docker container.

```bash
sapcli --ashost 172.17.0.2 --sysnr 00 --client 001 --user DEVELOPER --password Down1oad \
       startrfc STFC_CONNECTION '{"REQUTEXT":"ping"}'
```

If everything goes as expected you sould see the following outptu:

```
{'ECHOTEXT': 'ping', 'RESPTEXT': 'SAP R/3 Rel. 752   Sysid: NPL      Date: 20200223   Time: 231340   Logon_Data: 001/DEVELOPER/E'}
```

## Warning

This command is not available if [PyRFC](https://sap.github.io/PyRFC/index.html)
is not properly installed and you will not even see the parameter in the output
of _sapcli --help_.
