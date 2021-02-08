"""Fiori Launchpad initialization helper"""
import yaml

from sap import get_logger
from sap.flp.service import Service


class Builder:
    """FLP business objects initializer"""

    def __init__(self, connection, config_path):
        self._service = self._create_service(connection)
        self._config = self._load_config(config_path)

    def run(self):
        """Creates the business catalog"""

        get_logger().info("Running the cleanup")

        for catalog in self._config["catalogs"]:
            self._build_catalog(catalog)

        for group in self._config["groups"]:
            self._buid_group(group, self._config["catalogs"])

    def cleanup(self):
        """Removes existing catalogs and groups according to the configuration"""

        get_logger().info("Removing previously created catalogs")

        for catalog in self._config["catalogs"]:
            self._service.delete_catalog(catalog["id"])

        get_logger().info("Removing previously created groups")

        for group in self._config["groups"]:
            self._service.delete_group(group["id"])

    def _load_config(self, path):
        with open(path, 'r') as stream:
            return yaml.safe_load(stream)

    def _create_service(self, connection):
        return Service(connection)

    def _build_catalog(self, catalog):
        get_logger().info("Creating catalog: %s", catalog["title"])

        self._service.create_catalog({
            "domainId": catalog["id"],
            "title": catalog["title"]
        })

        for target_mapping in catalog["target_mappings"]:
            get_logger().info("Creating target mapping: %s", target_mapping["title"])

            self._service.create_mapping(catalog["id"], {
                "tileConfiguration": {
                    "semantic_object": target_mapping["semantic_object"],
                    "semantic_action": target_mapping["semantic_action"],
                    "display_title_text": target_mapping["title"],
                    "url": target_mapping["url"],
                    "ui5_component": target_mapping["ui5_component"]
                }
            })

        for tile in catalog["tiles"]:
            get_logger().info("Creating tile: %s", tile["title"])

            tile_reference = self._service.create_tile(catalog["id"], {
                "id": tile["id"],
                "tileConfiguration": {
                    "display_icon_url": tile["icon"],
                    "display_title_text": tile["title"],
                    "display_subtitle_text": tile.get("subtitle", ""),
                    "display_info_text": tile.get("info", ""),
                    "navigation_semantic_object": tile["semantic_object"],
                    "navigation_semantic_action": tile["semantic_action"],
                    "navigation_target_url": tile.get("url", f'#{tile["semantic_object"]}-{tile["semantic_action"]}'),
                },
                "title": tile["title"]
            })
            tile["instance_id"] = tile_reference.instanceId

    def _buid_group(self, group, catalogs):
        get_logger().info("Creating group: %s", group["title"])

        self._service.create_group({
            "id": group["id"],
            "title": group["title"]
        })

        for tile in group["tiles"]:
            get_logger().info("Adding tile: %s", tile["title"])

            catalog_tile = self._get_catalog_tile(catalogs, tile["catalog_id"], tile["catalog_tile_id"])

            self._service.add_tile_to_group(
                group_id=group["id"],
                catalog_id=tile["catalog_id"],
                tile_id=catalog_tile["instance_id"]
            )

    def _get_catalog_tile(self, catalogs, catalog_id, tile_id):
        for catalog in catalogs:
            if catalog["id"] == catalog_id:
                break

        for tile in catalog["tiles"]:
            if tile["id"] == tile_id:
                break

        return tile
