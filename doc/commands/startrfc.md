# startrfc

This command allows you to run an arbitrary RFC enabled Function Module.

```bash
sapcli startrfc --output={human,json} RFC_FUNCTION_MODULE {JSON_PARAMETERS,-} \
                [-I|--integer param:value] [-S|--string param:value]
                [-F|--file param:path]
```

* _--output_ allows you to specify format of the output
  * _human_ specifies format which suites human readers
  * _json_ specifies output in JSON

* _RFC\_FUNCION\_MODULE_ name of the executed Function Module

* _JSON\_PARAMETERS_ the call paremeters in the form of JSON object serialized
  into string; if - , then JSON string is read from standard input

* -I | --integer:  allows you to pass a numeric parameter of the executed RFC
  Function Module as a command line parameter. The value will overwrite value
  provided in JSON\_PARAMETERS or will be added if the parameter is not in present
  JSON\_PARAMETERS

* -S | --string:  allows you to pass a text parameter of the executed RFC
  Function Module as a command line parameter. The value will overwrite value
  provided in JSON\_PARAMETERS or will be added if the parameter is not in present
  JSON\_PARAMETERS

* -F | --file:  allows you to pass a binary parameter of the executed RFC
  Function Module as a command line parameter. The value path is used to open
  a file and its contents will be used as value of the RFC param.

* -c | --result-checker:  enables analysis of returned response
  * _raw_ the default value which does not do any analysis, just prints out the
     formatted response
  * _bapi_ stops printing out the retrieved response and instead tries to get
    the member *RETURN* from the response, expects the value is a table of the
    ABAP type *bapiret2* and prints out messages - if error message is
    found, only the error message is printed out and the process exists with
    non-0 exit code.

* -R | --response-file:  holds a file path where the complete response of the
  executed function module will be stored regardles of the result-checker's
  verdict. The format of the file is taken from the parameter '--output'.

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
