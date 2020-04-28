import argparse
import os

import alembic.command
from alembic.config import Config

import tikki
from tikki.app import app
from tikki.db import api as db_api


def _get_alembic_config() -> Config:
    path = os.path.join(os.path.dirname(tikki.__file__), 'alembic.ini')
    return Config(path)


def main():
    parser = argparse.ArgumentParser(description='Tikki application backend')
    parser.add_argument('-r', '--runserver', help='start the server', action='store_true')
    parser.add_argument('-m', '--migrate', help='run database migrations',
                        choices=['up', 'down'])
    parser.add_argument('-c', '--create', metavar='MESSAGE',
                        help='create a new database migration')
    parser.add_argument('-v', '--validate', help='check if server can be started',
                        action='store_true')

    args = parser.parse_args()
    if args.validate:
        print('validate')
        quit()
    elif args.create:
        alembic_cfg = _get_alembic_config()
        alembic.command.revision(alembic_cfg, args.create)
        quit()
    elif args.migrate:
        alembic_cfg = _get_alembic_config()
        if args.migrate == 'up':
            alembic.command.upgrade(alembic_cfg, 'head')
            db_api.regenerate_dimensions()
            db_api.regenerate_limits()
            db_api.regenerate_views()
        elif args.migrate == 'down':
            db_api.drop_metadata()
            alembic.command.downgrade(alembic_cfg, 'base')
        quit()
    elif args.runserver:
        app.run()

    parser.print_help()


if __name__ == "__main__":
    main()
