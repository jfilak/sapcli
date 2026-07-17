# sapcli supported configuration

sapcli can be configured via command line parameters, environment variables, and
a configuration file. The priority order from highest to lowest is:

1. **Command line arguments** - always win
2. **Environment variables** - override config file values
3. **Configuration file** (active context) - overrides defaults
4. **Built-in defaults** - used when nothing else is specified
5. **Interactive prompt** - fallback for mandatory values (user, password) when no SNC config is present, no valid OAuth token is cached, and no auth plugin or client certificate is configured

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

### --ssl-no-system-certs

By default sapcli validates server certificates against the operating system
trust store, so a root CA added via `update-ca-certificates` (see above), the
Windows Certificate Store or the macOS Keychain is honoured automatically. This
covers the sapcli HTTP traffic that targets the SAP system (ADT, REST/gCTS,
OData and OAuth token retrieval). It does not affect downloading a remote
configuration file (`--config <URL>`), because that download happens before the
connection options are resolved.

The switch `--ssl-no-system-certs` opts out and validates certificates against
the CA bundle shipped with the `certifi` package instead. The same behavior can
be achieved by setting the environment variable `SAP_SSL_USE_SYSTEM_CERTS` to a
false value (`no`, `false`, `off`) or the connection setting
`ssl_use_system_certs` to `false`.

The operating system trust store is not consulted when validation is disabled
(`--skip-ssl-validation`) or when an explicit CA bundle is supplied with
`--ssl-server-cert`; the explicit bundle then takes precedence.

This behavior relies on the
[truststore](https://pypi.org/project/truststore/) package, which is installed
automatically as a regular sapcli dependency. Should it ever be missing (an
incomplete installation), sapcli logs a warning and falls back to the bundled
certifi CA list.

Unlike `--skip-ssl-validation`, the operating system trust store keeps
certificate validation enabled - it only changes where the trusted CAs are read
from.

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

### --auth-plugin-invalidate-cache

Drop any cached auth-plugin response for the active context before
authenticating. The next command will re-run the configured plugin. Has
no effect unless an [auth plugin](#auth-plugins) is configured for the
active user.

```bash
sapcli --auth-plugin-invalidate-cache abap systeminfo
```

### --auth-plugin-disable-cache

Disable on-disk caching of the auth-plugin response entirely: sapcli
neither reads from nor writes to the cache, and any pre-existing entry
for the active context is deleted before the plugin runs.

Same behaviour can be achieved by setting the environment variable
`SAPCLI_AUTH_PLUGIN_DISABLE_CACHE` (to any non-false token), or by
adding `disable_cache: true` inside the `auth_plugin` mapping in the
config file. Precedence: CLI flag > env var > config file. The
[Response caching](#response-caching) section discusses the trade-off.

```bash
sapcli --auth-plugin-disable-cache abap systeminfo
```

### --auth-cert

Path to a PEM encoded X.509 client certificate used for TLS client
certificate authentication (mTLS) instead of user/password. The file may
also contain the private key - in that case `--auth-key` can be omitted.

When a client certificate is configured, sapcli does not prompt for user
or password - the server derives the user from the certificate.

The certificate can also be set via the environment variable
`SAP_AUTH_CERT` or via `auth_cert` in the configuration file. See
[Client certificate authentication](#client-certificate-authentication).

```bash
sapcli --auth-cert ~/certs/me.crt --auth-key ~/certs/me.key abap systeminfo
```

### --auth-key

Path to the PEM encoded private key belonging to `--auth-cert`. The key
must not be password protected - see
[Password protected keys](#password-protected-keys).

The key can also be set via the environment variable `SAP_AUTH_KEY` or
via `auth_key` in the configuration file.

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

A connection that uses OAuth 2.0 instead of a password is defined the same
way, with three additional fields:

```yaml
connections:
  my-cloud-system:
    ashost: my-tenant.abap.eu10.hana.ondemand.com
    client: "100"
    port: 443
    ssl: true
    token_url: https://my-tenant.authentication.eu10.hana.ondemand.com
    client_id: sb-abap!t12345
    client_secret: my-client-secret
```

See [OAuth 2.0 authentication](#oauth-20-authentication) below for details.

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
| `ssl_use_system_certs` | bool | no | `true` | `SAP_SSL_USE_SYSTEM_CERTS` |
| `mshost` | string | no (*) | - | `SAP_MSHOST` |
| `msserv` | string | no | - | `SAP_MSSERV` |
| `sysid` | string | no | - | `SAP_SYSID` |
| `group` | string | no | - | `SAP_GROUP` |
| `snc_qop` | string | no | - | `SNC_QOP` |
| `snc_myname` | string | no | - | `SNC_MYNAME` |
| `snc_partnername` | string | no | - | `SNC_PARTNERNAME` |
| `snc_lib` | string | no | - | `SNC_LIB` |
| `token_url` | string | no | - | `SAP_TOKEN_URL` |
| `client_id` | string | no | - | `SAP_CLIENT_ID` |
| `client_secret` | string | no | - | `SAP_CLIENT_SECRET` |

(*) Either `ashost` or `mshost` must be provided.

The `token_url`, `client_id`, and `client_secret` fields enable OAuth 2.0
authentication. See [OAuth 2.0 authentication](#oauth-20-authentication) below.

#### `users.<name>`

| Field | Type | Required | Default | Env var equivalent |
|---|---|---|---|---|
| `user` | string | yes (*) | - | `SAP_USER` |
| `password` | string | no | - | `SAP_PASSWORD` |
| `auth_plugin` | mapping | no | - | (config only) |
| `auth_cert` | string | no | - | `SAP_AUTH_CERT` |
| `auth_key` | string | no | - | `SAP_AUTH_KEY` |

(*) Not required when `auth_plugin` or `auth_cert` is used - the plugin
acquires the credentials itself and the server derives the user from a
client certificate.

`auth_plugin` is mutually exclusive with `password` and with OAuth fields
on the same logical session. See [Auth plugins](#auth-plugins) for the
plugin contract and configuration shape.

`auth_cert` is mutually exclusive with `password`, `auth_plugin`, and
OAuth fields supplied by the same source (command line, environment, or
configuration file). Across sources the higher-precedence one selects
the authentication mode - e.g. an exported `SAP_PASSWORD` wins over
`auth_cert` from the configuration file, while `--auth-cert` on the
command line wins over both. `auth_cert` and `auth_key` must come from
the same source. See
[Client certificate authentication](#client-certificate-authentication).

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

1. **Use a client certificate** - if your system supports X.509 logon,
   no password needs to be stored or exchanged (protect the unencrypted
   private key with restrictive file permissions). See
   [Client certificate authentication](#client-certificate-authentication) below.
2. **Use OAuth 2.0** - if your system supports it (e.g. SAP cloud systems),
   prefer OAuth over a stored password. See
   [OAuth 2.0 authentication](#oauth-20-authentication) below.
3. **Use an auth plugin** - for SAML2 SSO, certificates in secret stores,
   or any other method that does not fit OAuth or BasicAuth. See
   [Auth plugins](#auth-plugins) below.
4. **Omit the password from config** - sapcli will prompt interactively
5. **Use environment variables** - `SAP_PASSWORD` overrides the config file; suitable for CI/CD pipelines
6. **Store in config file** - acceptable for local development if the file has restrictive permissions (`chmod 600`)

sapcli will warn if the config file is world-readable and contains passwords.

The same caveats apply to `client_secret` when OAuth is used.

### OAuth 2.0 authentication

Some SAP systems — most notably SAP cloud systems such as SAP BTP ABAP
Environment ("Steampunk") — require OAuth 2.0 instead of a username/password
pair. sapcli can authenticate with OAuth and caches the obtained token
between commands so you do not need to log in every time.

#### Enabling OAuth

OAuth is enabled by setting three values on the connection definition, in
addition to your usual `--user`/`SAP_USER`:

| Field on `connections.<name>` | Env var | Description |
|---|---|---|
| `token_url` | `SAP_TOKEN_URL` | Base URL of the OAuth authorization server. sapcli appends `/oauth/token` automatically — provide the base, not the full endpoint. |
| `client_id` | `SAP_CLIENT_ID` | OAuth client ID issued by the system administrator. |
| `client_secret` | `SAP_CLIENT_SECRET` | OAuth client secret issued by the system administrator. |

These three values are not exposed as **global** command-line flags. They can
be provided via environment variables, written directly into the configuration
file under `connections.<name>` (see the YAML example in [Schema](#schema)),
or set with `sapcli config set-connection`:

```bash
sapcli config set-connection my-cloud-system \
    --token-url https://my-tenant.authentication.eu10.hana.ondemand.com \
    --client-id sb-abap!t12345 \
    --client-secret <secret>
```

These fields describe the OAuth **application** registration on the target
system, not the individual user — that is why they sit under `connections:`
alongside `ashost`/`port`, while your user name still belongs under `users:`.
A typical setup has one OAuth client per tenant, shared by all team members,
each with their own `users.<name>.user`.

#### How sapcli obtains a token

The first time you run a command against an OAuth-enabled connection, sapcli
asks the OAuth server for a token using your user name and password. This is
the only step that needs your password. After that, the token is cached in
`~/.sapcli/tokens.json` (file permissions `0600`) and reused by all subsequent
commands. When the token approaches expiration, sapcli refreshes it
transparently using a refresh token — no password is needed for the refresh.

If a valid cached token exists, sapcli does **not** prompt for a password,
even if `SAP_PASSWORD` is unset and the configuration file contains none.

If the OAuth server rejects your credentials or is unreachable, sapcli prints
an `OAuthTokenError` with the HTTP status code and the server's response
body. Verify `token_url`, `client_id`, `client_secret`, your user name, and
your password.

To force a fresh login (e.g. after rotating credentials), delete the cache
file:

```bash
rm ~/.sapcli/tokens.json
```

### Client certificate authentication

SAP systems can authenticate users with X.509 client certificates
(mutual TLS): the ICM maps the certificate's subject to an ABAP user, so
no password is exchanged at all. sapcli presents the certificate when
`--auth-cert`/`SAP_AUTH_CERT` or `auth_cert` in the configuration file
is set.

The certificate belongs to a **user** definition - it is an identity,
not a property of a system. One certificate is typically accepted by
many systems, which is expressed by referencing the same user from
several contexts:

```yaml
connections:
  dev-system:
    ashost: dev.example.com
    client: "100"

  qas-system:
    ashost: qas.example.com
    client: "200"

users:
  cert-me:                        # note: no 'user' name needed
    auth_cert: ~/certs/me.crt     # PEM certificate (may include the chain)
    auth_key: ~/certs/me.key      # PEM private key, not password protected

contexts:
  dev:
    connection: dev-system
    user: cert-me
  qas:
    connection: qas-system
    user: cert-me
```

Notes:

- When the certificate file also contains the private key, omit
  `auth_key` (the same convention as curl's `--cert` without `--key`).
- If the server requires intermediate issuer certificates, append them
  to the certificate file - there is no separate chain option.
- Validation of the *server's* certificate is unrelated to client
  certificate authentication and stays configured via
  `--ssl-server-cert`/`ssl_server_cert` or the operating system trust
  store.
- A client certificate requires TLS - combining it with `--no-ssl` is
  rejected.
- `--user` may still be supplied as a hint for systems that map one
  certificate to several users; it is optional.

#### Password protected keys

sapcli only accepts unencrypted private keys and refuses encrypted ones
with an error. Storing the key passphrase in the configuration file
would be equivalent to storing the key unencrypted, and prompting for
the passphrase on every command would be impractical for scripting.

Either decrypt the key into a file with restrictive permissions:

```bash
openssl pkey -in encrypted.key -out plain.key
chmod 600 plain.key
```

or use an [auth plugin](#auth-plugins) with the `certificates` response
type - a plugin can fetch the certificate from a secret store or decrypt
the key with a passphrase from a keyring and hand sapcli ephemeral
files.

### Auth plugins

Some authentication methods cannot reasonably be implemented inside
sapcli itself — SAML2 SSO requires running a browser, Windows client
certificates live in the Windows Certificate Store and cannot be
exported to a file, and a long tail of corporate IdPs each have their
own quirks. sapcli takes the kubectl approach for these cases: an
external command — the **auth plugin** — performs the authentication and
returns either cookies, an `Authorization` header, or a client
certificate. sapcli applies the result to the HTTP session and proceeds.

The plugin is invoked as a subprocess. sapcli writes a JSON request to
its stdin and reads a JSON response from its stdout. The plugin can be
implemented in any language and can pull in whatever dependencies it
needs — playwright for browser SSO, pywin32 for the Windows certificate
store, openssl shelled out from a bash script — without any of those
leaking into sapcli's installation.

The same auth plugin handles ADT, gCTS (REST), and OData commands. ABAP
session cookies are server-wide, so authenticating once primes the
cache for all three.

#### Enabling an auth plugin

Configure the plugin on a user definition:

```yaml
users:
  sso-user:
    auth_plugin:
      command: /absolute/path/to/your/plugin
      parameters:
        channel: msedge    # optional, plugin-specific key/value pairs
      disable_cache: false # optional, opt out of on-disk response caching
```

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `command` | string | yes | - | Absolute path to the plugin executable. |
| `parameters` | mapping | no | `{}` | Verbatim key/value pairs forwarded to the plugin as `parameters` in its stdin JSON. |
| `disable_cache` | bool | no | `false` | When true, sapcli does not write the plugin response to disk and ignores any existing entry. See [Response caching](#response-caching) for the env var and CLI flag overrides. |

`auth_plugin` is **mutually exclusive** with `password` and with the
OAuth fields on the same logical session — the plugin is the one source
of truth for credentials. sapcli rejects the configuration if both are
present.

`auth_plugin` is configured **only** in the config file, not via CLI
flags or environment variables. It is a structured value, not a scalar,
and its presence flips the entire authentication mode. (The
`disable_cache` knob inside it is the one exception — it can also be
set via `--auth-plugin-disable-cache` or `SAPCLI_AUTH_PLUGIN_DISABLE_CACHE`.)

#### Response caching

The first call to a plugin can be slow — browser-based SSO routinely
takes 20+ seconds while the user clicks through the IdP. sapcli caches
the response between invocations so subsequent commands run at sapcli's
native speed.

| Aspect | Value |
|---|---|
| Cache location (Linux) | `~/.local/state/sapcli/auth_plugin_responses/` |
| Cache location (macOS) | `~/Library/Application Support/sapcli/auth_plugin_responses/` |
| Cache location (Windows) | `%LOCALAPPDATA%\sapcli\auth_plugin_responses\` |
| Cache key | `<context>\|<connection>\|<user>` triple. Changing any of the three mints a new entry; identical triples share one entry across ADT, gCTS, and OData commands. |
| File permissions | Directory `0700`, file `0600` on POSIX. |
| Expiration | Honoured when the plugin's response includes an `expiration` ISO 8601 timestamp (with a 30 s leeway to avoid racing the server's clock). Plugins that omit it cache indefinitely; the server eventually invalidates the cached cookies and the next command falls back to a fresh plugin run. |

To force a fresh plugin run, pass `--auth-plugin-invalidate-cache` on
the command line:

```bash
sapcli --auth-plugin-invalidate-cache abap systeminfo
```

You can also delete the cache file directly — useful for scripted
cleanup.

##### Disabling the cache entirely

Some deployments cannot tolerate session credentials being written to
disk at all (corporate DLP policies, shared jump hosts, compliance
regimes that forbid at-rest persistence of bearer material). For those
cases, caching can be turned off altogether through any of the
following — in precedence order:

| Layer | How |
|---|---|
| CLI | `--auth-plugin-disable-cache` |
| Env var | `SAPCLI_AUTH_PLUGIN_DISABLE_CACHE=true` (any non-false token; `no`/`off`/`false`/`n` switch it back off) |
| Config | `auth_plugin.disable_cache: true` on the user definition |

When in effect, sapcli (1) does not read from the cache, (2) does not
write to it, and (3) deletes any pre-existing entry for the active
context before the plugin runs.

The trade-off: every sapcli invocation re-runs the plugin from scratch.
For browser-based SSO that is the difference between a sub-second
command and a 20-second one. Within a single sapcli invocation that
hits more than one connection type (ADT + gCTS + OData), the plugin is
re-invoked per connection — there is no in-process fallback today; this
is a known limitation when disabling the cache.

#### The plugin protocol

##### Request (stdin)

```json
{
  "connection": {
    "proto": "https",
    "ashost": "abap.example.org",
    "port": "44300",
    "client": "100",
    "type": "adt",
    "path": "/sap/bc/adt/core/discovery",
    "sysnr": null,
    "verify": true,
    "ssl_server_cert": null
  },
  "parameters": {
    "channel": "msedge"
  }
}
```

- `type` is one of `adt`, `rest`, `odata` — set by sapcli based on which
  command is running, so a plugin that supports multiple endpoints can
  pick the right one.
- `path` is the endpoint that sapcli's built-in flow uses for the same
  connection type. Use it unchanged unless your auth flow needs a
  different one.
- `verify` and `ssl_server_cert` mirror the `ssl_verify` and
  `ssl_server_cert` connection settings. Plugins must honour them when
  making HTTPS calls so they do not bypass the user's TLS policy.
- `parameters` is the verbatim `parameters:` map from the configuration
  — pass plugin-specific knobs through here.

##### Response (stdout)

```json
{
  "message": "Authentication successful",
  "expiration": "2026-05-08T23:59:59Z",
  "content": {
    "type": "cookie",
    "cookies": [
      {"name": "SAP_SESSIONID_X01_100", "value": "...", "domain": "abap.example.org", "path": "/", "secure": true}
    ]
  }
}
```

`content.type` selects the authentication mechanism applied to the HTTP
session. Three values are supported:

| `content.type` | Other fields | Effect on the session |
|---|---|---|
| `cookie` | `cookies: [{name, value, domain?, path?, expires?, secure?}, ...]` | Adds the cookies to `requests.Session.cookies`. |
| `http_authorization_header` | `headers: {<name>: <value>, ...}` | Sets the headers on the session (typically `Authorization`). |
| `certificates` | `certificate: <path>`, `key: <path>`, `issuer_certificate: <path>?` | Sets `session.cert` and optionally `session.verify` to the supplied file paths. |

`expiration` is optional. If present and ISO 8601, sapcli stops using
the cached response when the timestamp comes within 30 s of now and
re-runs the plugin. If absent, the response is cached indefinitely (the
server is the source of truth for invalidation).

##### Failure

A non-zero exit code from the plugin means authentication failed.
sapcli prints the plugin's `message` field (if it emitted valid JSON on
stdout), along with the captured stdout and stderr, and stops. A plugin
that prints invalid JSON on stdout is treated the same way.

#### Reference plugin

sapcli ships a proof-of-concept plugin at
`plugins/auth/basic-auth-cookies.py` that performs HTTP Basic auth and
returns the resulting session cookies. It exists primarily to exercise
the protocol end-to-end against a real ABAP system without needing a
browser-automation plugin set up, and to serve as a template for
writing your own. Credentials are read from `SAP_USER` and
`SAP_PASSWORD` environment variables so they never appear in the config
file.

```yaml
users:
  basic-auth-via-plugin:
    auth_plugin:
      command: /absolute/path/to/sapcli/plugins/auth/basic-auth-cookies.py
```

```bash
SAP_USER=DEVELOPER SAP_PASSWORD=secret \
    sapcli --context my-system abap systeminfo
```

#### Writing your own plugin

A plugin is any executable that:

1. Reads a single JSON object from stdin (the request shape above).
2. Performs authentication using whatever mechanism it needs.
3. Writes a single JSON object to stdout (the response shape above).
4. Exits 0 on success or non-zero on failure.

There is no required language, library, or interface to import — the
contract is the JSON envelope on stdin/stdout, full stop. Look at
`plugins/auth/basic-auth-cookies.py` for a minimal Python example. A
browser-based SSO plugin would replace the `requests.get` call with a
`playwright.sync_api` flow that opens a window, waits for the user to
log in, and reads cookies out of the resulting browser context.

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

### Managing connections

```bash
# Create a new connection
sapcli config set-connection dev-server --ashost dev.example.com --client 100 --port 443 --ssl

# Update an existing connection (only specified fields change, others preserved)
sapcli config set-connection dev-server --port 8443

# Add OAuth 2.0 credentials to a connection (see "OAuth 2.0 authentication" below)
sapcli config set-connection cloud-srv \
    --token-url https://auth.example.com \
    --client-id sb-app!t12345 \
    --client-secret my-client-secret

# List all connections
sapcli config get-connections

# Delete a connection (blocked if referenced by contexts)
sapcli config delete-connection dev-server

# Force delete even if referenced
sapcli config delete-connection dev-server --force
```

### Managing users

```bash
# Create a new user
sapcli config set-user dev-user --user DEVELOPER

# Update a user (add or change password)
sapcli config set-user dev-user --password secret

# List all users
sapcli config get-users

# Delete a user (blocked if referenced by contexts)
sapcli config delete-user dev-user

# Force delete even if referenced
sapcli config delete-user dev-user --force
```

### Managing contexts

```bash
# Create a context linking a connection and user
sapcli config set-context dev --connection dev-server --user dev-user

# Update a context with field overrides
sapcli config set-context qa --connection dev-server --user dev-user --ashost qa.example.com

# Add a password override to a context
sapcli config set-context prod --password prod-secret

# Delete a context (unsets current-context if it pointed here)
sapcli config delete-context qa
```

All `set-*` commands use **upsert semantics**: they create the entry if it
does not exist, or merge the provided fields into the existing entry. Fields
not specified on the command line are preserved (patch/merge behavior).

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
- `SAP_SSL_USE_SYSTEM_CERTS` : SSL server certificates are validated against the
   operating system trust store by default; set this to a false value (no, false,
   off - case insensitive) to fall back to the bundled certifi CA list
- `SAP_TOKEN_URL` : base URL of the OAuth 2.0 authorization server; corresponds to `connections.<name>.token_url` (enables OAuth authentication; see [OAuth 2.0 authentication](#oauth-20-authentication))
- `SAP_CLIENT_ID` : OAuth 2.0 client ID; corresponds to `connections.<name>.client_id`
- `SAP_CLIENT_SECRET` : OAuth 2.0 client secret; corresponds to `connections.<name>.client_secret`
- `SAP_CORRNR` : if a sapcli command accepts parameter '--corrnr', you can provide default value via this environment variable
- `SAPCLI_CONFIG` : path to the configuration file (overrides the default `~/.sapcli/config.yml`)
- `SAPCLI_CONTEXT` : name of the context to use (overrides `current-context` in the config file; overridden by `--context` CLI flag)
- `SAPCLI_LOG_LEVEL` : pass the desired log level - the lower number the more
  messages (`CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0`)
- `SAPCLI_HTTP_TIMEOUT` : floating point number representing timeout for HTTP requests; default=900s
- `SAPCLI_ABAP_USER_DUMMY_PASSWORD` : string representing a dummy password which is used as a temporary password when changing user's password to productive; default='DummyPwd123!'
- `SAPCLI_CHECK_BEFORE_SAVE` : enables the ADT `abapCheckRun` reporter
  on the candidate source before any sapcli command writes it to the
  server. The intent is to give agentic workflows (Claude Code and
  similar) automatic syntax validation by setting the variable once at
  session start; humans get the default fast path with no extra HTTP
  round-trip. Accepts `1`, `true`, `yes`, `on` (enable) and `0`,
  `false`, `no`, `off` (disable), case-insensitive. Per-command
  semantics:
    - `sapcli class write` and the other write commands: the
      pre-check is **off by default**. Set the variable to `true` to
      turn it on for every invocation, or pass `--check` /
      `--no-check` to override on a single call. Independently of the
      variable, a failed write is always re-run through
      `abapCheckRun` so the user gets a readable diagnostic instead
      of the cryptic ADT save error.
    - `sapcli checkin package`: same opt-in semantics; abapGit
      repositories are usually already syntactically clean so the
      pre-check is wasted work in the typical case.
    - `sapcli abap run`: the pre-check is **on by default** because
      the wrapper class is generated by sapcli; setting the variable
      to `false` is the escape hatch when the check itself misfires.
