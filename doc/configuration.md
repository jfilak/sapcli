# sapcli supported configuration

sapcli can be configured command line parameter, environment variables, and
through configuration file where command line has the highest priority and
configuration file the lowest priority.

## Parameters

| Command line | Environment | Configuration file | Default | Description
| ------------ | ----------- | ------------------ | ------- | ------------------------- |
| --ashost     | SAP_ASHOST  |                    | | Host name or IP address of the application server |
| --client     | SAP_CLIENT  |                    | | SAP Client number - default 001 |
| --no-ssl     | SAP_SSL     |                    | On | Turns off SSL for ADT  - default SSL is on |
| --port       | SAP_PORT    |                    | 443 | Sets ADT HTTP port - default 443 |
| --user       | SAP_USER     |                    | prompt | User login |
| --password   | SAP_PASSWORD |                    | prompt | User password |
