# sapcli supported configuration

sapcli can be configured via command line parameters, environment variables, and
a configuration file. The priority order from highest to lowest is:

1. **Command line arguments** - always win
2. **Environment variables** - override config file values
3. **Configuration file** (active context) - overrides defaults
4. **Built-in defaults** - used when nothing else is specified
5. **Interactive prompt** - fallback for mandatory values (user, password) when no SNC config is present

## Parameters

### --ashost

Name of the host where your SAP Application Server exposes ADT ICF service.

The value can be DNS name or IP address.

This parameter is mandatory and must be provided either on the command line
or as the environment variable `SAP_ASHOST`.

### --sysnr

ABAP system instance number.

This parameter is optional and can be provided either on the command line
or as the environment variable `SAP_SYSNR`.

The default value of this parameter is 00 (i.e. the port 3200).

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

### --config

Path to an alternative configuration file.

Overrides the `SAPCLI_CONFIG` environment variable and the default
`~/.sapcli/config.yml`.

```bash
sapcli --config /path/to/custom-config.yml program read ZREPORT
```

### --context

Select which context from the config file to use for this invocation.

Overrides the `SAPCLI_CONTEXT` environment variable and `current-context` in the config file.

```bash
sapcli --context prod program read ZREPORT
```

## Configuration file

### File location

The configuration file is looked up in the following order:

1. Path specified by `--config` CLI flag
2. Path in the `SAPCLI_CONFIG` environment variable
3. `~/.sapcli/config.yml` (default)

On Linux/macOS, the default path expands to `/home/<user>/.sapcli/config.yml`
(or `/Users/<user>/.sapcli/config.yml` on macOS). On Windows, it expands to
`C:\Users\<user>\.sapcli\config.yml`.

### File format

YAML. It is human-readable, widely used for configuration, and supports comments.

### Schema

The configuration file uses a kubeconfig-style model with three top-level concepts:

- **connection** - defines how to reach a SAP system (host, port, client, SSL settings)
- **user** - defines authentication credentials (username, and optionally password)
- **context** - binds a connection to a user, with optional field overrides

```yaml
# ~/.sapcli/config.yml

# Current active context (used when --context and SAPCLI_CONTEXT are not specified)
current-context: dev

# Connection definitions
connections:
  dev-server:
    ashost: dev-system.example.com
    client: "100"
    port: 443
    ssl: true
    ssl_verify: true
    sysnr: "00"

  # A base connection template (no ashost - provided by contexts)
  sap-standard:
    client: "100"
    port: 443
    ssl: true
    ssl_verify: true
    sysnr: "00"

# User definitions
users:
  dev-user:
    user: DEVELOPER

  prod-user:
    user: DEPLOYER

# Context definitions (bind a connection to a user)
contexts:
  dev:
    connection: dev-server
    user: dev-user

  # Contexts can override any connection or user field.
  # This allows sharing a single connection definition across
  # multiple systems that differ only in a few fields:
  qa:
    connection: sap-standard
    user: dev-user
    ashost: qa-system.example.com      # overrides connection

  prod:
    connection: sap-standard
    user: prod-user
    ashost: prod-system.example.com    # overrides connection
    password: prod-secret              # overrides user
```

### Field reference

#### `connections.<name>`

| Field | Type | Required | Default | Env var equivalent |
|---|---|---|---|---|
| `ashost` | string | yes (*) | - | `SAP_ASHOST` |
| `sysnr` | string | no | `"00"` | `SAP_SYSNR` |
| `client` | string | yes | - | `SAP_CLIENT` |
| `port` | int | no | `443` | `SAP_PORT` |
| `ssl` | bool | no | `true` | `SAP_SSL` |
| `ssl_verify` | bool | no | `true` | `SAP_SSL_VERIFY` |
| `ssl_server_cert` | string | no | - | `SAP_SSL_SERVER_CERT` |
| `mshost` | string | no (*) | - | `SAP_MSHOST` |
| `msserv` | string | no | - | `SAP_MSSERV` |
| `sysid` | string | no | - | `SAP_SYSID` |
| `group` | string | no | - | `SAP_GROUP` |
| `snc_qop` | string | no | - | `SNC_QOP` |
| `snc_myname` | string | no | - | `SNC_MYNAME` |
| `snc_partnername` | string | no | - | `SNC_PARTNERNAME` |
| `snc_lib` | string | no | - | `SNC_LIB` |
| `http_timeout` | float | no | `900` | `SAPCLI_HTTP_TIMEOUT` |

(*) Either `ashost` or `mshost` must be provided.

#### `users.<name>`

| Field | Type | Required | Default | Env var equivalent |
|---|---|---|---|---|
| `user` | string | yes | - | `SAP_USER` |
| `password` | string | no | - | `SAP_PASSWORD` |

#### `contexts.<name>`

| Field | Type | Required | Default |
|---|---|---|---|
| `connection` | string | yes | - |
| `user` | string | yes | - |

A context can also contain any field from `connections.<name>` and
`users.<name>.password` as an inline override. When specified, the
context-level value takes precedence over the referenced connection or user
definition. For example:

```yaml
contexts:
  qa:
    connection: sap-standard
    user: dev-user
    ashost: qa-system.example.com   # overrides sap-standard.ashost
    port: 8443                      # overrides sap-standard.port
    password: qa-secret             # overrides dev-user.password
```

This is useful when many systems share the same configuration except for a few
fields (e.g. hostname). Define one base connection and override per context.

### Credentials handling

Storing passwords in plain text configuration files is a security concern.
The recommended approaches, in order of preference:

1. **Omit the password from config** - sapcli will prompt interactively
2. **Use environment variables** - `SAP_PASSWORD` overrides the config file; suitable for CI/CD pipelines
3. **Store in config file** - acceptable for local development if the file has restrictive permissions (`chmod 600`)

sapcli will warn if the config file is world-readable and contains passwords.

## Config management commands

```bash
# Show the current effective configuration
sapcli config view

# Show the current context name
sapcli config current-context

# Switch the active context
sapcli config use-context prod

# List available contexts
sapcli config get-contexts

# Merge a shared configuration file into your config
sapcli config merge --source /shared/team-connections.yml

# Merge from an HTTPS URL
sapcli config merge --source https://config.company.com/sapcli/common.yml

# Merge and overwrite existing entries
sapcli config merge --source /shared/team-connections.yml --overwrite

# Merge from an HTTP URL (not recommended)
sapcli config merge --source http://internal-server/config.yml --insecure

# Merge from HTTPS without certificate validation (e.g. self-signed cert)
sapcli --skip-ssl-validation config merge --source https://internal-server/config.yml
```

### Merging configuration files

The `merge` command allows you to incorporate connection details from a shared
configuration file into your personal config. This is useful for onboarding
new users or distributing common system connection details across a team.

**Merge semantics:**

- The `connections`, `users`, and `contexts` sections are merged additively.
- Existing entries with the same name are **not overwritten** by default. Your
  personal config always wins. Use `--overwrite` to replace existing entries.
- Your `current-context` is never changed by the merge.
- The command prints a summary of what was added and what was skipped.

**Source types:**

- **Local file path**: any file path on the local filesystem.
- **HTTPS URL**: a remote configuration file served over HTTPS. Plain HTTP
  is rejected for security reasons.

**Security notes:**

- Shared configuration files should not contain passwords. The command will
  warn if the source file contains credentials.
- Remote sources must use HTTPS. Plain HTTP URLs are rejected unless
  `--insecure` is passed, which should only be used for trusted internal
  networks.
- For HTTPS servers with self-signed certificates or CA trust issues (common
  on Windows), use the global `--skip-ssl-validation` flag to skip certificate
  verification:
  ```bash
  sapcli --skip-ssl-validation config merge --source https://internal-server/config.yml
  ```

## Context selection precedence

The active context is determined in the following order:

1. `--context` CLI flag (highest priority)
2. `SAPCLI_CONTEXT` environment variable
3. `current-context` from the configuration file (lowest priority)

Using `SAPCLI_CONTEXT` is convenient when working in multiple shells
targeting different systems. It also composes well with tools like
[direnv](https://direnv.net/) for per-directory context selection.

## Environment variables

- `SAP_ASHOST` : default value for the command line parameter --ashost
- `SAP_SYSNR` : default value for the command line parameter --sysnr
- `SAP_CLIENT` : default value for the command line parameter --client
- `SAP_SSL` : negative default value for the command line parameter --no-ssl
   and accepts the values no, false, off; where all other values are considered as True;
   the value parser is case insensitive
- `SAP_PORT` : default value for the command line parameter --port
- `SAP_USER` : default value for the command line parameter --user
- `SAP_PASSWORD` : default value for the command line parameter --password
- `SAP_SSL_SERVER_CERT` : path to the public unencrypted server SSL certificate
- `SAP_SSL_VERIFY` : if "no", SSL server certificate is no validated - this works only when SAP_SSL_SERVER_CERT is not configured
- `SAP_CORRNR` : if a sapcli command accepts parameter '--corrnr', you can provide default value via this environment variable
- `SAPCLI_CONFIG` : path to the configuration file (overrides the default `~/.sapcli/config.yml`)
- `SAPCLI_CONTEXT` : name of the context to use (overrides `current-context` in the config file; overridden by `--context` CLI flag)
- `SAPCLI_LOG_LEVEL` : pass the desired log level - the lower number the more
  messages (`CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0`)
- `SAPCLI_HTTP_TIMEOUT` : floating point number representing timeout for HTTP requests; default=900s
- `SAPCLI_ABAP_USER_DUMMY_PASSWORD` : string representing a dummy password which is used as a temporary password when changing user's password to productive; default='DummyPwd123!'
