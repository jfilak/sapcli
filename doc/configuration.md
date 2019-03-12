# sapcli supported configuration

sapcli can be configured command line parameter, environment variables, and
through configuration file where command line has the highest priority and
configuration file the lowest priority.

## Parameters

### --ashost

Name of the host where your SAP Application Server exposes ADT ICF service.

The value can be DNS name or IP address.

This parameter is mandatory and must be provided either on the command line
or as the environment variable `SAP_ASHOST`.

### --client

SAP client number in the standard form with the leading zeros.

This parameter is mandatory and must be provided either on the command line
or as the environment variable `SAP_CLIENT`.

### --no-ssl

By default, sapcli tries to communicate using HTTPS in URLs and this parameters
allows you to switch to HTTP (without SSL).

This parameter is mandatory and must be provided either on the command line or
as the environment variable `SAP_SSL` (beware the environment variable values
is positive, while the command line parameter is negative).

### --skip-ssl-validation

Danger! Skipping certificate validation may expose your secure communication to
eavesdropping and other man-in-the-middle attacks. Use with care!

By default, sapcli tries to validate SSL certificates against the list of known
root CAs. For servers with self-signed SSL certificates or certificates issued
by a self-signed CA you should normally add them to your system's CA
certificates. On Linux this works like that:

```
$ sudo cp your-server.crt /usr/local/share/ca-certificates
$ sudo update-ca-certificates
```

In development environments or in case of problems with your certificates, you
can use the switch `--skip-ssl-validation` to suppress all certificate checks
when connecting to your server. Same behavior can be achieved by setting the
environment variable `SAP_SSL_VERIFY` to `no`.

### --port

TCP PORT where your SAP Application Server accepts connection for ICF services.

This parameter is optional where the default value is 443 for communication
with SSL and 80 for communication without SSL.

You an change the port number also via the environment variable SAP_PORT.

### --user

Your SAP user ALIAS.

This parameter is mandatory and if you do not provided it on the command line
or as the environment variable `SAP_USER`, sapcli will prompt you for it.

### --password

Your SAP user's password.

This parameter is mandatory and if you do not provided it on the command line
or as the environment variable `SAP_PASSWORD`, sapcli will prompt you for it.

## Environment variables

- `SAP_ASHOST` : default value for the command line parameter --ashost
- `SAP_CLIENT` : default value for the command line parameter --client
- `SAP_SSL` : negative default value for the command line parameter --no-ssl
   and accepts the values no, false, off; where all other values are considered as True;
   the value parser is case insensitive
- `SAP_PORT` : default value for the command line parameter --port
- `SAP_USER` : default value for the command line parameter --user
- `SAP_PASSWORD` : default value for the command line parameter --password
- `SAP_SSL_SERVER_CERT` : path to the public unencrypted server SSL certificate
- `SAP_SSL_VERIFY` : if "no", SSL server certificate is no validated - this works only when SAP_SSL_SERVER_CERT is not configured
