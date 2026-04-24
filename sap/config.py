"""Configuration"""

import os
import stat
import warnings
from pathlib import Path
from typing import Any, Optional

import requests
import yaml

from sap.errors import SAPCliError


DEFAULT_CONFIG_PATH = os.path.join('~', '.sapcli', 'config.yml')


class SAPCliConfigError(SAPCliError):
    """Exception type for configuration errors"""


CONNECTION_FIELDS = (
    'ashost', 'sysnr', 'client', 'port', 'ssl', 'ssl_verify',
    'ssl_server_cert', 'mshost', 'msserv', 'sysid', 'group',
    'snc_qop', 'snc_myname', 'snc_partnername', 'snc_lib',
)

USER_FIELDS = (
    'user', 'password',
)

CONTEXT_FIELDS = ()

# Fields that can be overridden at context level (excludes the
# structural 'connection' and 'user' reference keys)
CONTEXT_OVERRIDE_FIELDS = CONNECTION_FIELDS + USER_FIELDS + CONTEXT_FIELDS


def _resolve_config_path(cli_config_path: Optional[str] = None) -> Path:
    """Resolve the config file path based on precedence:
       1. --config CLI flag
       2. SAPCLI_CONFIG environment variable
       3. ~/.sapcli/config.yml (default)

       Always returns the resolved Path, even if the file does not exist.
    """

    if cli_config_path:
        return Path(cli_config_path).expanduser()

    env_path = os.environ.get('SAPCLI_CONFIG')
    if env_path:
        return Path(env_path).expanduser()

    return Path(DEFAULT_CONFIG_PATH).expanduser()


def _check_file_permissions(path: Path) -> None:
    """Warn if the config file is world-readable and contains passwords."""

    try:
        file_stat = os.stat(path)
        mode = file_stat.st_mode
        if mode & stat.S_IROTH:
            warnings.warn(
                f'Configuration file {path} is world-readable. '
                'Consider restricting permissions with: chmod 600 '
                f'{path}',
                UserWarning,
                stacklevel=3
            )
    except OSError:
        pass


def _load_config_file(path: Path) -> dict:
    """Load and parse a YAML config file."""

    try:
        with open(path, 'r', encoding='utf-8') as config_file:
            try:
                data = yaml.safe_load(config_file)
            except yaml.YAMLError as ex:
                raise SAPCliConfigError(
                    f'Failed to parse configuration file {path}: {ex}'
                ) from ex
    except OSError as ex:
        raise SAPCliConfigError(
            f'Failed to read configuration file {path}: {ex}'
        ) from ex

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise SAPCliConfigError(
            f'Configuration file {path} does not contain a valid YAML mapping'
        )

    return data


def _has_passwords(config_data: dict) -> bool:
    """Check if the config contains any password fields."""

    users = config_data.get('users', {})
    if isinstance(users, dict):
        for user_def in users.values():
            if isinstance(user_def, dict) and user_def.get('password'):
                return True

    contexts = config_data.get('contexts', {})
    if isinstance(contexts, dict):
        for context_def in contexts.values():
            if isinstance(context_def, dict) and context_def.get('password'):
                return True

    return False


class ConfigFile:
    """Represents a loaded sapcli configuration file."""

    def __init__(self, data: dict, path: Path):
        self._data = data
        self._path = path

    @staticmethod
    def load(cli_config_path: Optional[str] = None) -> 'ConfigFile':
        """Load configuration from file. Returns an empty ConfigFile
           if no config file is found.
        """

        path = _resolve_config_path(cli_config_path)
        if not path.is_file():
            # If the user explicitly supplied a path (CLI flag or env var)
            # and it exists but is not a regular file, that's an error.
            explicitly_supplied = cli_config_path or os.environ.get('SAPCLI_CONFIG')
            if explicitly_supplied and path.exists():
                raise SAPCliConfigError(
                    f"Config path is not a regular file: '{path}'"
                )
            return ConfigFile({}, path)

        data = _load_config_file(path)

        _validate_config_data(data, f'Configuration file {path}')

        if _has_passwords(data):
            _check_file_permissions(path)

        return ConfigFile(data, path)

    @property
    def path(self) -> Path:
        """Returns the path of the config file."""
        return self._path

    @property
    def data(self) -> dict:
        """Returns the raw config data."""
        return self._data

    @property
    def current_context(self) -> Optional[str]:
        """Returns the current-context name from config."""
        return self._data.get('current-context')

    @current_context.setter
    def current_context(self, value: str) -> None:
        """Sets the current-context name."""
        self._data['current-context'] = value

    @property
    def connections(self) -> dict:
        """Returns the connections section."""
        return self._data.get('connections', {})

    @property
    def users(self) -> dict:
        """Returns the users section."""
        return self._data.get('users', {})

    @property
    def contexts(self) -> dict:
        """Returns the contexts section."""
        return self._data.get('contexts', {})

    def get_context(self, context_name: str) -> dict:
        """Returns a specific context definition.
           Raises SAPCliConfigError if the context does not exist
           or the config structure is malformed.
        """

        contexts = self.contexts
        if not isinstance(contexts, dict):
            raise SAPCliConfigError(
                'Configuration \'contexts\' section is not a valid mapping'
            )

        if context_name not in contexts:
            raise SAPCliConfigError(
                f'Context \'{context_name}\' not found in configuration file'
            )

        context = contexts[context_name]
        if not isinstance(context, dict):
            raise SAPCliConfigError(
                f'Context \'{context_name}\' is not a valid mapping'
            )

        return context

    def get_connection(self, connection_name: str) -> dict:
        """Returns a specific connection definition.
           Raises SAPCliConfigError if the connection does not exist
           or the config structure is malformed.
        """

        connections = self.connections
        if not isinstance(connections, dict):
            raise SAPCliConfigError(
                'Configuration \'connections\' section is not a valid mapping'
            )

        if connection_name not in connections:
            raise SAPCliConfigError(
                f'Connection \'{connection_name}\' not found in configuration file'
            )

        connection = connections[connection_name]
        if not isinstance(connection, dict):
            raise SAPCliConfigError(
                f'Connection \'{connection_name}\' is not a valid mapping'
            )

        return connection

    def get_user(self, user_name: str) -> dict:
        """Returns a specific user definition.
           Raises SAPCliConfigError if the user does not exist
           or the config structure is malformed.
        """

        users = self.users
        if not isinstance(users, dict):
            raise SAPCliConfigError(
                'Configuration \'users\' section is not a valid mapping'
            )

        if user_name not in users:
            raise SAPCliConfigError(
                f'User \'{user_name}\' not found in configuration file'
            )

        user = users[user_name]
        if not isinstance(user, dict):
            raise SAPCliConfigError(
                f'User \'{user_name}\' is not a valid mapping'
            )

        return user

    def resolve_context(self, context_name: Optional[str] = None) -> Optional[dict]:
        """Resolve the effective context. Returns a flat dict with
           all connection, user, and context-level settings merged.

           If context_name is None, uses the current-context from config.
           Returns None if no context is available.
        """

        if context_name is None:
            context_name = self.current_context

        if context_name is None:
            return None

        context = self.get_context(context_name)

        connection_name = context.get('connection')
        if not connection_name:
            raise SAPCliConfigError(
                f'Context \'{context_name}\' does not specify a connection'
            )

        user_name = context.get('user')
        if not user_name:
            raise SAPCliConfigError(
                f'Context \'{context_name}\' does not specify a user'
            )

        connection = self.get_connection(connection_name)
        user = self.get_user(user_name)

        result = {}

        # Connection fields
        for field in CONNECTION_FIELDS:
            if field in connection:
                result[field] = connection[field]

        # User fields
        for field in USER_FIELDS:
            if field in user:
                result[field] = user[field]

        # Context-level overrides (any connection, user, or context field
        # specified directly on the context definition wins).
        # Skip 'connection' and 'user' as these are structural reference
        # keys in the context, not override values.
        for field in CONTEXT_OVERRIDE_FIELDS:
            if field not in ('connection', 'user') and field in context:
                result[field] = context[field]

        return result

    def _ensure_section(self, section: str) -> dict:
        """Ensure a top-level section exists and return it."""

        if section not in self._data:
            self._data[section] = {}

        value = self._data[section]
        if not isinstance(value, dict):
            raise SAPCliConfigError(
                f'Configuration \'{section}\' section is not a valid mapping'
            )

        return value

    def set_connection(self, name: str, fields: dict) -> None:
        """Create or merge-update a named connection.

        If the connection exists, only the provided fields are updated
        (merge/patch semantics). If it does not exist, a new entry is
        created with the provided fields.
        """

        connections = self._ensure_section('connections')

        if name in connections:
            if not isinstance(connections[name], dict):
                connections[name] = {}
            connections[name].update(fields)
        else:
            connections[name] = dict(fields)

    def set_user(self, name: str, fields: dict) -> None:
        """Create or merge-update a named user."""

        users = self._ensure_section('users')

        if name in users:
            if not isinstance(users[name], dict):
                users[name] = {}
            users[name].update(fields)
        else:
            users[name] = dict(fields)

    def set_context(self, name: str, fields: dict) -> None:
        """Create or merge-update a named context."""

        contexts = self._ensure_section('contexts')

        if name in contexts:
            if not isinstance(contexts[name], dict):
                contexts[name] = {}
            contexts[name].update(fields)
        else:
            contexts[name] = dict(fields)

    def find_referencing_contexts(self, section: str, name: str) -> list:
        """Return a list of context names that reference the given
        connection or user by name.

        section must be 'connection' or 'user' (the key used inside
        context definitions to reference the named entry).
        """

        if section not in ('connection', 'user'):
            raise ValueError(
                f"section must be 'connection' or 'user', got '{section}'"
            )

        contexts = self.contexts
        if not isinstance(contexts, dict):
            return []

        refs = []
        for ctx_name, ctx_def in contexts.items():
            if isinstance(ctx_def, dict) and ctx_def.get(section) == name:
                refs.append(ctx_name)

        return refs

    def delete_connection(self, name: str, force: bool = False) -> None:
        """Delete a named connection.

        Raises SAPCliConfigError if the connection does not exist or is
        referenced by contexts (unless force=True).
        """

        connections = self.connections
        if name not in connections:
            raise SAPCliConfigError(
                f'Connection \'{name}\' not found in configuration file'
            )

        if not force:
            refs = self.find_referencing_contexts('connection', name)
            if refs:
                raise SAPCliConfigError(
                    f'Cannot delete connection \'{name}\': '
                    f'referenced by contexts: {", ".join(refs)}'
                )

        del self._data['connections'][name]

    def delete_user(self, name: str, force: bool = False) -> None:
        """Delete a named user.

        Raises SAPCliConfigError if the user does not exist or is
        referenced by contexts (unless force=True).
        """

        users = self.users
        if name not in users:
            raise SAPCliConfigError(
                f'User \'{name}\' not found in configuration file'
            )

        if not force:
            refs = self.find_referencing_contexts('user', name)
            if refs:
                raise SAPCliConfigError(
                    f'Cannot delete user \'{name}\': '
                    f'referenced by contexts: {", ".join(refs)}'
                )

        del self._data['users'][name]

    def delete_context(self, name: str) -> None:
        """Delete a named context.

        Raises SAPCliConfigError if the context does not exist.
        If current-context points to the deleted context, it is unset.
        """

        contexts = self.contexts
        if name not in contexts:
            raise SAPCliConfigError(
                f'Context \'{name}\' not found in configuration file'
            )

        del self._data['contexts'][name]

        if self.current_context == name:
            del self._data['current-context']

    def save(self, path: Optional[Path] = None) -> None:
        """Save the configuration to file."""

        save_path = path or self._path

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as ex:
            raise SAPCliConfigError(
                f'Failed to create directory for configuration file {save_path}: {ex}'
            ) from ex

        try:
            fd = os.open(save_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as config_file:
                yaml.dump(self._data, config_file, default_flow_style=False, sort_keys=False)
        except OSError as ex:
            raise SAPCliConfigError(
                f'Failed to write configuration file {save_path}: {ex}'
            ) from ex
        except yaml.YAMLError as ex:
            raise SAPCliConfigError(
                f'Failed to serialize configuration to {save_path}: {ex}'
            ) from ex

        self._path = save_path


MERGEABLE_SECTIONS = ('connections', 'users', 'contexts')


def _validate_config_data(data, label: str) -> None:
    """Validate that data is a dict with dict-valued mergeable sections."""

    if not isinstance(data, dict):
        raise SAPCliConfigError(
            f'{label} does not contain a valid YAML mapping'
        )

    for section in MERGEABLE_SECTIONS:
        value = data.get(section)
        if value is not None and not isinstance(value, dict):
            raise SAPCliConfigError(
                f'{label} section \'{section}\' is not a valid mapping'
            )


def merge_into(target: 'ConfigFile', source_data: dict,
               overwrite: bool = False) -> dict:
    """Merge source config data into target ConfigFile.

    Merges the connections, users, and contexts sections additively.
    Returns a summary dict with 'added' and 'skipped' keys, each
    mapping section names to lists of entry names.
    """

    _validate_config_data(source_data, 'Source configuration')

    summary: dict[str, dict[str, list[str]]] = {
        'added': {s: [] for s in MERGEABLE_SECTIONS},
        'skipped': {s: [] for s in MERGEABLE_SECTIONS},
    }

    for section in MERGEABLE_SECTIONS:
        source_section = source_data.get(section, {})
        if not source_section:
            continue

        if section not in target.data:
            target.data[section] = {}

        target_section = target.data[section]

        for name, value in source_section.items():
            if name in target_section and not overwrite:
                summary['skipped'][section].append(name)
            else:
                target_section[name] = value
                summary['added'][section].append(name)

    return summary


def fetch_config_source(source: str, insecure: bool = False,
                        ssl_verify: bool = True) -> dict:
    """Load config data from a local file path or HTTPS/HTTP URL.

    Raises SAPCliConfigError on errors (network, parsing, validation).
    Plain HTTP URLs are rejected unless insecure=True.
    When ssl_verify=False, HTTPS certificate validation is skipped.
    """

    if source.startswith('http://'):
        if not insecure:
            raise SAPCliConfigError(
                f'Plain HTTP is not allowed for security reasons: {source}\n'
                'Use HTTPS or pass --insecure to allow plain HTTP.'
            )
        return _fetch_config_from_url(source, ssl_verify=True)

    if source.startswith('https://'):
        return _fetch_config_from_url(source, ssl_verify=ssl_verify)

    return _fetch_config_from_path(source)


def _fetch_config_from_url(url: str, ssl_verify: bool = True) -> dict:
    """Fetch and parse config data from an HTTP(S) URL."""

    try:
        response = requests.get(url, timeout=30, verify=ssl_verify)
        response.raise_for_status()
    except requests.RequestException as ex:
        raise SAPCliConfigError(
            f'Failed to fetch configuration from {url}: {ex}'
        ) from ex

    try:
        data = yaml.safe_load(response.text)
    except yaml.YAMLError as ex:
        raise SAPCliConfigError(
            f'Failed to parse configuration from {url}: {ex}'
        ) from ex

    if data is None:
        data = {}

    _validate_config_data(data, f'Remote configuration {url}')

    if _has_passwords(data):
        warnings.warn(
            f'Source configuration from {url} contains passwords. '
            'Shared configuration files should not contain credentials.',
            UserWarning,
            stacklevel=2
        )

    return data


def _fetch_config_from_path(source: str) -> dict:
    """Load and parse config data from a local file path."""

    path = Path(source).expanduser()

    if not path.is_file():
        raise SAPCliConfigError(
            f'Source configuration file not found: {path}'
        )

    data = _load_config_file(path)

    _validate_config_data(data, f'Source configuration {path}')

    if _has_passwords(data):
        warnings.warn(
            f'Source configuration file {path} contains passwords. '
            'Shared configuration files should not contain credentials.',
            UserWarning,
            stacklevel=2
        )

    return data


_TRUTHY_ENV_VALUES = {'1', 'true', 'yes', 'on'}
_FALSY_ENV_VALUES = {'0', 'false', 'no', 'off'}


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment variable.

    Accepts the usual spellings (1/0, true/false, yes/no, on/off) in a
    case-insensitive way. Unknown values fall back to ``default`` - we
    do not fail a whole CLI invocation over a typo in an optional flag.
    """

    raw = os.environ.get(name)
    if raw is None:
        return default

    normalised = raw.strip().lower()
    if normalised in _TRUTHY_ENV_VALUES:
        return True
    if normalised in _FALSY_ENV_VALUES:
        return False
    return default


def config_get(option: str, default: Any = None) -> Any:
    """Returns configuration values"""

    config = {
        'http_timeout': float(os.environ.get('SAPCLI_HTTP_TIMEOUT', 900)),
        'check_before_save': _env_bool('SAPCLI_CHECK_BEFORE_SAVE', True),
    }

    return config.get(option, default)
