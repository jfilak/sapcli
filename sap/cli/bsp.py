"""bsp methods"""

import base64
import json
import pprint
import pyodata
import sap.cli.core
import sap.cli.helpers

from sap import get_logger
from sap.errors import ResourceAlreadyExistsError


class CommandGroup(sap.cli.core.CommandGroup):
    """Management for BSP Applications"""

    def __init__(self):
        super().__init__('bsp')


@CommandGroup.argument('--bsp', type=str, required=True, help='BSP ID')
@CommandGroup.argument('--package', type=str, required=True, help='ABAP Package')
@CommandGroup.argument('--app', type=str, required=True, help='Path to application packed in zip archive')
@CommandGroup.argument('--corrnr', type=str, required=True,
                       help='Transport Request to be used for application upload')
@CommandGroup.command()
def create(connection, args):
    """Creates the requested BSP application.

       Important: Target ABAP system needs following setup

       * update trnspace set editflag = 'X' role = 'P' license = '' sscrflag = 'X'
         where namespace = '/0CUST/' or namespace = '/0SAP/'.
       * table /IWFND/C_CONFIG je 'GATEWAY_VIRUSCAN_PROFILE'='-'
    """

    # load zipped application from filesystem
    with open(args.app, 'rb') as file:
        app_data_archive = file.read()

    # convert raw zipped data to base54 encoding
    app_data_b64 = base64.b64encode(app_data_archive)

    # check if application exists
    try:
        connection.client.entity_sets.Repositories.get_entity(Name=args.bsp).execute()
        raise ResourceAlreadyExistsError
    except pyodata.exceptions.HttpError as ex:
        if ex.response.status_code != 404:
            raise ex

    app_data = {
        'Name': args.bsp,
        'Package': args.package,
        'ZipArchive': app_data_b64.decode("utf-8"),
    }

    create_request = connection.client \
        .entity_sets \
        .Repositories \
        .create_entity() \
        .custom('CodePage', 'UTF8') \
        .custom('TransportRequest', args.corrnr) \
        .custom('client', args.client)

    create_request.set(**app_data)

    try:
        create_request.execute()
    except pyodata.exceptions.HttpError as ex:
        res = json.loads(ex.response.text)
        get_logger().info(pprint.pformat(res))
        raise ex

    get_logger().info('BSP application successfully created and uploaded')


@CommandGroup.argument('--bsp', type=str, required=True, help='BSP ID')
@CommandGroup.command()
def stat(connection, args):
    """Get information about BSP application"""

    console = sap.cli.core.get_console()

    # check if application exists
    try:
        bsp = connection.client.entity_sets.Repositories.get_entity(Name=args.bsp).execute()
    except pyodata.exceptions.HttpError as ex:
        if ex.response.status_code == 404:
            return sap.cli.core.EXIT_CODE_NOT_FOUND
        else:
            raise ex

    console.printout(f'Name                   :{bsp.Name}')
    console.printout(f'Package                :{bsp.Package}')
    console.printout(f'Description            :{bsp.Description}')

    return sap.cli.core.EXIT_CODE_OK


@CommandGroup.argument('--bsp', type=str, required=True, help='BSP ID')
@CommandGroup.argument('--corrnr', type=str, required=True,
                       help='Transport Request to be used for application removal')
@CommandGroup.command()
def delete(connection, args):
    """Get information about BSP application"""

    try:
        connection.client \
            .entity_sets \
            .Repositories \
            .delete_entity(Name=args.bsp) \
            .custom('TransportRequest', args.corrnr) \
            .execute()
    except pyodata.exceptions.HttpError as ex:
        if ex.response.status_code != 404:
            raise ex

    get_logger().info('BSP application successfully removed')
