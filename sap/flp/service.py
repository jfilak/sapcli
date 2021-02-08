"""Fiori Launchpad initialization helper"""

import json


class Service:
    """FLP business objects initializer"""

    def __init__(self, connection):
        self._connection = connection

    def create_catalog(self, data):
        """Creates a new business catalog"""

        create_request = self._connection.client.entity_sets.Catalogs.create_entity()
        create_request.set(
            **data,
            type="CATALOG_PAGE"
        )

        return create_request.execute()

    def create_group(self, data):
        """Creates a new applications group"""

        create_request = self._connection.client.entity_sets.Pages.create_entity()
        create_request.set(
            **data,
            catalogId="/UI2/FLPD_CATALOG",
            layout=""
        )

        return create_request.execute()

    def create_tile(self, catalog_id, data):
        """Creates a new app tile"""

        create_request = self._connection.client.entity_sets.PageChipInstances.create_entity()
        create_request.set(
            chipId="X-SAP-UI2-CHIP:/UI2/STATIC_APPLAUNCHER",
            scope="CUSTOMIZING",
            instanceId="",
            layoutData="",
            pageId=f"X-SAP-UI2-CATALOGPAGE:{catalog_id}",
            title=data["title"],
            configuration=json.dumps({
                "id": data["id"],
                "tileConfiguration": json.dumps({
                    "navigation_use_semantic_object": True,
                    "navigation_semantic_parameters": "",
                    "display_search_keywords": "",
                    **data["tileConfiguration"]
                })
            })
        )

        return create_request.execute()

    def create_mapping(self, catalog_id, data):
        """Creates a new target mapping"""

        create_request = self._connection.client.entity_sets.PageChipInstances.create_entity()
        create_request.set(
            chipId="X-SAP-UI2-CHIP:/UI2/ACTION",
            configuration=json.dumps({
                "tileConfiguration": json.dumps({
                    "navigation_provider": "SAPUI5",
                    "navigation_provider_role": "",
                    "navigation_provider_instance": "",
                    "target_application_id": "",
                    "target_application_alias": "",
                    "transaction": {
                        "code": ""
                    },
                    "web_dynpro": {
                        "application": "",
                        "configuration": ""
                    },
                    "target_system_alias": "",
                    "display_info_text": "",
                    "mapping_signature": "*=*",
                    "signature": {
                        "parameters": {
                            "": {
                                "required": False
                            }
                        },
                        "additional_parameters": "allowed"
                    },
                    **data["tileConfiguration"]
                })
            }),
            scope="CUSTOMIZING",
            instanceId="",
            layoutData="",
            pageId=f"X-SAP-UI2-CATALOGPAGE:{catalog_id}",
            title=""
        )

        return create_request.execute()

    def add_tile_to_group(self, group_id, catalog_id, tile_id):
        """Adds a tile to the group"""

        create_request = self._connection.client.entity_sets.PageChipInstances.create_entity()
        create_request.set(
            chipId=f"X-SAP-UI2-PAGE:X-SAP-UI2-CATALOGPAGE:{catalog_id}:{tile_id}",
            pageId=group_id
        )

        return create_request.execute()

    def delete_catalog(self, catalog_id):
        """Removes exising catalog"""

        catalogs = self._connection.client.entity_sets.Catalogs.get_entities().filter(f"domainId eq '{catalog_id}'").execute()

        for catalog in catalogs:
            self._connection.client.entity_sets.Catalogs.delete_entity(key=catalog.entity_key).execute()

    def delete_group(self, group_id):
        """Removes existing group"""
        self._connection.client.entity_sets.Pages.delete_entity(group_id).execute()
