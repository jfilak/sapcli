# user

This command set allows you to create, read, and modify users in AS ABAP
systems. This functinaly requires RFC connectivity.

1. [details](#details)
2. [create](#create)
3. [change](#change)

## details

Prints out very limited list of user parameters retrieved from the configured
system.

```bash
sapcli user details USERNAME
```

**Parameters**:
- `USERNAME`: the specified user

## create

Creates the specified user with the given parameters.

```bash
sapcli user create [--type Dialog|Service|System] [--new-password PASSWORD] USERNAME
```

**Parameters**:
- `USERNAME`: the created user
- `--new-password PASSWORD`: the created user's new password
- `--type Dialog|Service|System`: the type of the created user

## change

Modifies the specified user with the given parameters.
Currently, it can change only the password.

```bash
sapcli user modify [--new-password PASSWORD] USERNAME
```

**Parameters**:
- `USERNAME`: the specified user
- `--new-password PASSWORD`: the user's new password
