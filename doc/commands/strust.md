# strust

This command allows basic operations on SAP certificates store. It allows to
upload or list X.509 certificates, which are used for SSL peer verification
of remote servers

1. [putcertificate](#putcertificate)
2. [listcertificates](#listcertificates)
2. [dumpcertificates](#dumpcertificates)

## putcertificate

Uploads certificate to the SAP system from local filesystem. File shall be encoded
as bas64 X.509 certificate

```bash
sapcli strust putcertificate --store client_standard ./cert.pem"
```

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
