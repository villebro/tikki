import os

import argparse

from tikki.app import app
from tikki.db import api as db_api
import tikki

parser = argparse.ArgumentParser(description='Tikki application backend')
parser.add_argument('-r', '--runserver', help='start the server', action='store_true')
parser.add_argument('-m', '--migrate', help='run database migrations',
                    choices=['up', 'down'])
parser.add_argument('-v', '--validate', help='check if server can be started',
                    action='store_true')

args = parser.parse_args()
if args.validate:
    print('validate')
    quit()
elif args.migrate:
    from alembic.config import Config
    from alembic import command

    path = os.path.join(os.path.dirname(tikki.__file__), 'alembic.ini')
    print(path)
    alembic_cfg = Config(path)
    if args.migrate == 'up':
        command.upgrade(alembic_cfg, 'head')
        db_api.regenerate_dimensions()
        db_api.regenerate_limits()
        db_api.regenerate_views()
    elif args.migrate == 'down':
        db_api.drop_metadata()
        command.downgrade(alembic_cfg, 'base')
    quit()
elif args.runserver:
    app.run()

parser.print_help()
