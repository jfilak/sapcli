'''FLP Builder tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import json
import yaml
import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, call, mock_open, patch
from sap.flp.builder import Builder
from fixtures_flp_builder import FLP_BUILDER_CONFIG


@patch('builtins.open', mock_open(read_data=FLP_BUILDER_CONFIG))
class TestFlpBuilder(unittest.TestCase):
    '''Test FLP Builder'''

    def test_init_ok(self):
        connection = MagicMock()
        instance = Builder(connection, "config")

        self.assertDictEqual(instance._config, yaml.safe_load(FLP_BUILDER_CONFIG))
        open.assert_called_with("config", "r")

    def test_cleanup_ok(self):
        def get_catalogs():
            catalogs = [Mock(), Mock()]
            catalogs[0].entity_key = "C1"
            catalogs[1].entity_key = "C2"
            return catalogs

        connection = MagicMock()
        instance = Builder(connection, "config")

        connection.client.entity_sets.Catalogs.get_entities().filter().execute.side_effect = get_catalogs
        connection.client.entity_sets.Pages.delete_entity().execute = Mock()

        instance.cleanup()

        catalog_calls = connection.client.entity_sets.Catalogs.delete_entity.call_args_list

        self.assertIn(call(key="C1"), catalog_calls)
        self.assertIn(call(key="C2"), catalog_calls)

        connection.client.entity_sets.Pages.delete_entity.assert_called_with("ZCUSTOM_GROUP")

    def test_run_ok(self):
        def create_tile():
            tile_instance = Mock()
            tile_instance.instanceId = "TILE_ID"
            return tile_instance

        connection = MagicMock()
        instance = Builder(connection, "config")

        connection.client.entity_sets.PageChipInstances.create_entity().execute.side_effect = create_tile

        instance.run()

        # Create catalog
        connection.client.entity_sets.Catalogs.create_entity().set.assert_called_with(
            domainId="ZCUSTOM_CATALOG",
            title="Custom Catalog",
            type="CATALOG_PAGE"
        )

        # Create group
        connection.client.entity_sets.Pages.create_entity().set.assert_called_with(
            id="ZCUSTOM_GROUP",
            title="Custom Group",
            catalogId="/UI2/FLPD_CATALOG",
            layout=""
        )

        page_chip_instance_calls = connection.client.entity_sets.PageChipInstances.create_entity().set.call_args_list

        # Create target mapping
        args, kwargs = page_chip_instance_calls[0]
        tile_config = json.loads(json.loads(kwargs["configuration"])["tileConfiguration"])

        self.assertEqual(kwargs["chipId"], "X-SAP-UI2-CHIP:/UI2/ACTION")
        self.assertEqual(kwargs["pageId"], "X-SAP-UI2-CATALOGPAGE:ZCUSTOM_CATALOG")
        self.assertEqual(tile_config["navigation_provider"], "SAPUI5")
        self.assertEqual(tile_config["semantic_object"], "MyReporting")
        self.assertEqual(tile_config["semantic_action"], "display")
        self.assertEqual(tile_config["display_title_text"], "My Reporting App")
        self.assertEqual(tile_config["url"], "/sap/bc/ui5_ui5/sap/ZMY_REPORT")
        self.assertEqual(tile_config["ui5_component"], "zmy.app.reporting")

        # Create tile
        args, kwargs = page_chip_instance_calls[1]
        tile_config = json.loads(json.loads(kwargs["configuration"])["tileConfiguration"])

        self.assertEqual(kwargs["chipId"], "X-SAP-UI2-CHIP:/UI2/STATIC_APPLAUNCHER")
        self.assertEqual(kwargs["pageId"], "X-SAP-UI2-CATALOGPAGE:ZCUSTOM_CATALOG")
        self.assertEqual(kwargs["title"], "My Reporting App")
        self.assertEqual(tile_config["navigation_use_semantic_object"], True)
        self.assertEqual(tile_config["display_icon_url"], "sap-icon://settings")
        self.assertEqual(tile_config["display_title_text"], "My Reporting App")
        self.assertEqual(tile_config["display_subtitle_text"], "")
        self.assertEqual(tile_config["display_info_text"], "")
        self.assertEqual(tile_config["navigation_semantic_object"], "MyReporting")
        self.assertEqual(tile_config["navigation_semantic_action"], "display")
        self.assertEqual(tile_config["navigation_target_url"], "#MyReporting-display")

        # Add tile to group
        args, kwargs = page_chip_instance_calls[2]
        self.assertEqual(kwargs["chipId"], "X-SAP-UI2-PAGE:X-SAP-UI2-CATALOGPAGE:ZCUSTOM_CATALOG:TILE_ID")
        self.assertEqual(kwargs["pageId"], "ZCUSTOM_GROUP")
