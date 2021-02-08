# Fiori Launchpad

1. [init](#init)

## init

Initializes the Fiori Launchpad based on the YAML configuration file

```bash
sapcli flp init --config ./config.yml
```

Example configuration:

```yaml
catalogs:
  - title: Custom Catalog
    id: ZCUSTOM_CATALOG
    target_mappings:
      - title: My Reporting App
        semantic_object: MyReporting
        semantic_action: display
        url: /sap/bc/ui5_ui5/sap/ZMY_REPORT # path to the BSP app on the SAP system
        ui5_component: zmy.app.reporting # UI5 app id defined in manifest.json
    tiles:
      - title: My Reporting App
        id: ZMY_REPORTING
        icon: sap-icon://settings
        semantic_object: MyReporting
        semantic_action: display
groups:
  - title: Custom Group
    id: ZCUSTOM_GROUP
    tiles:
      - title: My Reporting App
        catalog_id: ZCUSTOM_CATALOG
        catalog_tile_id: ZMY_REPORTING # this has to match one of the catalogs->tiles->id property
```
