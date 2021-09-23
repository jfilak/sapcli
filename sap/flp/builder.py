"""Fiori Launchpad initialization helper"""
import yaml

from sap import get_logger
from sap.flp.service import Service
from sap.errors import SAPCliError


def _create_service(connection):
    return Service(connection)


def _load_config(path):
    with open(path, 'r', encoding='utf8') as stream:
        return yaml.safe_load(stream)


class CatalogTileError(Exception):
    """Just be able to raise the right exception from
       the function searching for Title.
    """

    # pylint: disable=unnecessary-pass
    pass


def _get_catalog_tile(catalogs, catalog_id, tile_id):
    catalog = next((item for item in catalogs if item['id'] == catalog_id), None)
    if catalog is None:
        raise CatalogTileError(f'Catalogue {catalog_id} was not found')

    try:
        return next((item for item in catalog['tiles'] if item['id'] == tile_id))
    except StopIteration:
        # pylint: disable=raise-missing-from
        raise CatalogTileError(f'Tile {tile_id} was not found in Catalog {catalog_id}')


class Builder:
    """FLP business objects initializer"""

    def __init__(self, connection, config_path):
        self._service = _create_service(connection)
        self._config = _load_config(config_path)

    def run(self):
        """Creates the business catalog"""

        get_logger().info('Running the cleanup')

        for catalog in self._config['catalogs']:
            self._build_catalog(catalog)

        for group in self._config['groups']:
            self._buid_group(group, self._config['catalogs'])

    def cleanup(self):
        """Removes existing catalogs and groups according to the configuration"""

        get_logger().info('Removing previously created catalogs')

        for catalog in self._config['catalogs']:
            self._service.delete_catalog(catalog['id'])

        get_logger().info('Removing previously created groups')

        for group in self._config['groups']:
            self._service.delete_group(group['id'])

    def _build_catalog(self, catalog):
        get_logger().info('Creating catalog: %s', catalog['title'])

        self._service.create_catalog({
            'domainId': catalog['id'],
            'title': catalog['title']
        })

        for target_mapping in catalog['target_mappings']:
            get_logger().info('Creating target mapping: %s', target_mapping['title'])

            self._service.create_mapping(catalog['id'], {
                'tileConfiguration': {
                    'semantic_object': target_mapping['semantic_object'],
                    'semantic_action': target_mapping['semantic_action'],
                    'display_title_text': target_mapping['title'],
                    'url': target_mapping['url'],
                    'ui5_component': target_mapping['ui5_component']
                }
            })

        for tile in catalog['tiles']:
            get_logger().info('Creating tile: %s', tile['title'])

            tile_reference = self._service.create_tile(catalog['id'], {
                'id': tile['id'],
                'tileConfiguration': {
                    'display_icon_url': tile['icon'],
                    'display_title_text': tile['title'],
                    'display_subtitle_text': tile.get('subtitle', ''),
                    'display_info_text': tile.get('info', ''),
                    'navigation_semantic_object': tile['semantic_object'],
                    'navigation_semantic_action': tile['semantic_action'],
                    'navigation_target_url': tile.get('url', f"#{tile['semantic_object']}-{tile['semantic_action']}"),
                },
                'title': tile['title']
            })
            tile['instance_id'] = tile_reference.instanceId

    def _buid_group(self, group, catalogs):
        get_logger().info('Creating group: %s', group['title'])

        self._service.create_group({
            'id': group['id'],
            'title': group['title']
        })

        for tile in group['tiles']:
            get_logger().info('Adding tile: %s', tile['title'])

            try:
                catalog_tile = _get_catalog_tile(catalogs, tile['catalog_id'], tile['catalog_tile_id'])
            except CatalogTileError as ex:
                raise SAPCliError(f"Failed to add tile {tile['title']} to group {group['title']}") from ex

            self._service.add_tile_to_group(
                group_id=group['id'],
                catalog_id=tile['catalog_id'],
                tile_id=catalog_tile['instance_id']
            )
