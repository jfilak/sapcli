# Feature Toggles

sapcli provides commands to manage SAP Feature Toggles (SFW).

1. [state](#state)
2. [on](#on)
3. [off](#off)

## state

Get the current state of a feature toggle.

```bash
sapcli featuretoggle state ID
```

**Parameters**:
- `ID`: Feature Toggle identifier

The command prints the client state and user state of the feature toggle.

**Example output**:
```
Client 100: off
User DEVELOPER: undefined
```

## on

Enable a feature toggle.

```bash
sapcli featuretoggle on ID --corrnr CORRNR
```

**Parameters**:
- `ID`: Feature Toggle identifier
- `--corrnr CORRNR`: Transport Request to capture Feature Toggle changes (required)

## off

Disable a feature toggle.

```bash
sapcli featuretoggle off ID --corrnr CORRNR
```

**Parameters**:
- `ID`: Feature Toggle identifier
- `--corrnr CORRNR`: Transport Request to capture Feature Toggle changes (required)
