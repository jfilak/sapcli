# strust

This command allows basic operations on SAP certificates store. It allows to list,
create or remove PSEs, and upload or list X.509 certificates, which are used
for SSL peer verification of remote servers.

STRUST Identity consists of `PSE Context` and `PSE Application`. Consequently, there are
defined multiple `Storages` which are used as aliases for Identities.

List of available `Storages`:
- `server_standard`:
  - PSE context: `SSLS`
  - PSE application: `DFAULT`
- `client_anonymous`:
  - PSE context: `SSLC`
  - PSE application: `ANONYM`
- `client_standard`:
  - PSE context: `SSLC`
  - PSE application: `SSLC`

1. [list](#list)
2. [createpse](#createpse)
3. [removepse](#removepse)
2. [createidentity](#createidentity)
4. [getcsr](#getcsr)
5. [putpkc](#putpkc)
6. [upload](#upload)
7. [putcertificate](#putcertificate)
8. [listcertificates](#listcertificates)
9. [dumpcertificates](#dumpcertificates)

## list

List all existing STRUST identities.

```bash
sapcli strust list
```

## createpse

Creates a new (or replaces an existing) PSE.

```bash
sapcli strust createpse [-i|--identity IDENTITY] [-s|--storage STORAGE] [--dn DN] [-k|--key-length KEY_LENGTH] [-l|--algorithm ALGORITHM] [--overwrite]
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**
- `--dn`: Distinguished Name (LDAP DN) of PSE. **(optional)**
- `--key-length`: Key Length of PSE file, default is `2048`. **(optional)**
- `--algorithm`: PSE file Encryption algorithm, default is `RSAwithSHA256`. **(optional)**
- `--overwrite`: Overwrite the existing PSE file, default is `False`. **(optional)**

## removepse

Deletes PSE based on STRUST identity.

```bash
sapcli strust removepse [-i|--identity IDENTITY] [-s|--storage STORAGE]
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**

## createidentity

Creates a new (or replaces an existing) STRUSTR Identity. The description will be store under the current users
language settings.

```bash
sapcli strust createidentity [-i|--identity IDENTITY] [-s|--storage STORAGE] [-d|--description DESCRIPTION] [--overwrite]
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**
- `--description`: Identity Description. **(optional)**
- `--overwrite`: Overwrite the existing Identity, default is `False`. **(optional)**

# getcsr

Prints out Certificate Signing Request.

```bash
sapcli strust getcsr [-i|--identity IDENTITY] [-s|--storage STORAGE]
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**

## putpkc

Uploads Identity Certificate.

```bash
sapcli strust putpkc [-i|--identity IDENTITY] [-s|--storage STORAGE] PATH
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**
- `PATH`: Path to the file containing the certificate (multiple can be specified), or `-` to read from `standard input`.

## upload

Uploads complete PSE file (and possibly replaces an existing PSE).

```bash
sapcli strust upload [-i|--identity IDENTITY] [-s|--storage STORAGE] [--pse-password PASSWORD] [--ask-pse-password] [--overwrite] PATH
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**
- `--pse-password`: PSE export password. **(optional)**
- `--aks-pse-password`: Ask for PSE export password. Ignored when password is specified using `--pse-password`. **(optional)**
- `--overwrite`: Overwrite the existing PSE file, default is `False`. **(optional)**
- `PATH`: Path to the PSE file in the form of `PKCS#12 (*.pfx)`.

## putcertificate

Puts the given certificate onto list of trusted certificates of the give PSE.
The certificate can be passed from local filesystem or read from input stream.
Both the file and data in input stream shall be PEM encoded X.509 certificate.

```bash
sapcli strust putcertificate [-i|--identity IDENTITY] [-s|--storage STORAGE] [-a|--algorithm ALGORITHM] [-k|--key-length KEYLEGNTH] [-d|--dn DN] [-|PATH ...]
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**
- `--algorithm`: Algorithm used to create a new PSE if the requeste does not exist
- `--key-length`: Key-length used to create a new PSE if the requeste does not exist
- `--dn`: Distinguished Name used to create a new PSE if the requeste does not exist
- `PATH`: Path to the certificate files in the form PEM encoded X.509.
- `-`: if the symbol dash is used instead of PATH, the certifate will be read from STDIN

## getowncert

Prints out PSE certificate in the form PEM encoded X.509.

```bash
sapcli strust getowncert [-i|--identity IDENTITY] [-s|--storage STORAGE]
```

**Parameters**:
- `--identity`: STRUST identity (PSE context + PSE application). **(Mutually exclusive with the option --storage)**
- `--storage`: Predefined STRUST identities. **(Mutually exclusive with the option --identity)**

## listcertificates

Lists (briefly) all certificates from specified identities and stores.

```bash
sapcli strust listcertificates --store client_standard"
```

## dumpcertificates

Dumps all certificates from specified identities and stores in PEM format.

```bash
sapcli strust dumpcertificates --store client_standard"
```

And this is how to process pem output in shell (`csplit` and `openssl` commands
have to be available). Each certificate will be stored as single file:

```bash
# output dump to a file
sapcli strust listcertificate --store client_standard > certs.pem

# split into files - one file per one certificate
csplit -s -z -f cert- certs.pem '/-----BEGIN CERTIFICATE-----/' '{*}'

# show issuer and expiration date for each certificatte
for $f in cert-* do; cat $f | openssl x509 -issuer -enddate -noout; done 
```
were:
* `-s` skips printing output of file sizes
* `-z` does not create empty files


# Deprecated
- Storage `client_standart` is replaced by `client_standard` (fixed typo)
