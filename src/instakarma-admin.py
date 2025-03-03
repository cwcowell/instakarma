import os
import sys

if os.path.basename(os.getcwd()) != 'src':
    print("Error: 'instakarma-admin' must be run from the '<REPO-ROOT-DIR>/src/' directory")
    sys.exit(1)

from constants import *
from db_mgr import DbMgr
from entity_mgr import EntityMgr
from enums import Status
from grant_mgr import GrantMgr
from karma_mgr import KarmaMgr
from log_mgr import LogMgr
from message_parser import MessageParser
from string_mgr import StringMgr

import argparse
from argparse import ArgumentParser
from logging import Logger
import sqlite3
import sys


def init_db() -> None:
    """Initialize the DB.

    No-op if the DB already exists.

    :raises SystemExit: If there are DB errors
    """

    result: str = ''
    try:
        db_manager.init_db()
    except sqlite3.Error as e:
        raise SystemExit(StringMgr.get_string('error.sqlite3', e=e))


def set_status(name: str, new_status: Status) -> None:
    """Set the opted-in/opted-out status of an entity.

    Also prints the entity's new status.

    Intended to be called from `instakarma-admin` only.

    :raises SystemExit: If there are DB errors or the entity doesn't exist in the DB
    """

    try:
        if not entity_manager.name_exists_in_db(name):
            sys.exit(StringMgr.get_string('instakarma-admin.no-entity-exists', name=name))
        entity_manager.set_status(name, new_status)
    except sqlite3.Error as e:
        sys.exit(StringMgr.get_string('error.sqlite3', e=e))
    print(StringMgr.get_string('instakarma-admin.current-status',
                               name=name,
                               status=entity_manager.get_status(name).value))


def main() -> None:
    """Parse CLI parameters and handle each valid parameter."""

    parser: ArgumentParser = argparse.ArgumentParser(
        description=StringMgr.get_string('instakarma-admin.description'),
        prog=StringMgr.get_string('instakarma-admin.prog'),
        epilog=StringMgr.get_string('instakarma-admin.epilog'))

    subparsers = parser.add_subparsers(dest='command')

    add_entity_parser = subparsers.add_parser('add-entity',
                                              help=StringMgr.get_string('instakarma-admin.help.add-entity.command'))
    add_entity_parser.add_argument('name',
                                   help=StringMgr.get_string('instakarma-admin.help.add-entity.name-var'),
                                   metavar='NAME')

    subparsers.add_parser('backup-db', help=StringMgr.get_string('instakarma-admin.help.backup-db'))
    subparsers.add_parser('export-grants', help=StringMgr.get_string('instakarma-admin.help.export-grants'))
    subparsers.add_parser('list-by-karma', help=StringMgr.get_string('instakarma-admin.help.list-by-karma'))
    subparsers.add_parser('list-by-name', help=StringMgr.get_string('instakarma-admin.help.list-by-name'))
    subparsers.add_parser('list-opted-out', help=StringMgr.get_string('instakarma-admin.help.list-opted-out'))

    opt_in_parser = subparsers.add_parser('opt-in',
                                          help=StringMgr.get_string('instakarma-admin.help.opt-in.command'))
    opt_in_parser.add_argument('name',
                               help=StringMgr.get_string('instakarma-admin.help.opt-in.name-var'),
                               metavar='NAME')

    opt_out_parser = subparsers.add_parser('opt-out',
                                           help=StringMgr.get_string('instakarma-admin.help.opt-out.command'))
    opt_out_parser.add_argument('name',
                                help=StringMgr.get_string('instakarma-admin.help.opt-out.name-var'),
                                metavar='NAME')

    args: argparse.Namespace = parser.parse_args()

    # print help if no command is provided
    if not args.command:
        parser.print_help()
        sys.exit(1)

    match args.command:
        case 'add-entity':
            name: str = args.name
            try:
                if entity_manager.name_exists_in_db(name):
                    sys.exit(StringMgr.get_string('instakarma-admin.add-entity.failed', name=name))
                entity_manager.add_entity(name, None)
            except sqlite3.Error as e:
                sys.exit(StringMgr.get_string('error.sqlite3', e=e))
            print(StringMgr.get_string('instakarma-admin.add-entity.successful', name=name))

        case 'backup-db':
            db_manager.backup_db()

        case 'export-grants':
            grant_manager.export_grants()

        case 'list-by-karma':
            try:
                entities = entity_manager.list_entities('karma')
            except sqlite3.Error as e:
                sys.exit(StringMgr.get_string('error.sqlite3', e=e))
            for name, karma in entities:
                print(f"{karma},{name}")

        case 'list-by-name':
            try:
                entities = entity_manager.list_entities('name')
            except sqlite3.Error as e:
                sys.exit(StringMgr.get_string('error.sqlite3', e=e))
            for name, karma in entities:
                print(f"{name},{karma}")

        case 'list-opted-out':
            try:
                entities = entity_manager.list_opted_out_entities()
            except sqlite3.Error as e:
                sys.exit(StringMgr.get_string('error.sqlite3', e=e))
            if not entities:
                print(StringMgr.get_string('instakarma-admin.nobody-opted-out'))
            for name in entities:
                print(name)

        case 'opt-in':
            set_status(args.name, Status.OPTED_IN)

        case 'opt-out':
            set_status(args.name, Status.OPTED_OUT)


if __name__ == '__main__':
    logger: Logger = LogMgr.get_logger(LOGGER_NAME,
                                       LOG_FILE,
                                       LOG_LEVEL,
                                       LOG_FILE_SIZE,
                                       LOG_FILE_COUNT)
    db_manager: DbMgr = DbMgr(logger)
    entity_manager: EntityMgr = EntityMgr(db_manager, logger)
    karma_manager: KarmaMgr = KarmaMgr(db_manager, entity_manager, logger)
    message_parser: MessageParser = MessageParser(logger)
    grant_manager: GrantMgr = GrantMgr(entity_manager, karma_manager, logger, message_parser, db_manager)

    init_db()  # error handling is easier there's a DB guaranteed to be present
    main()
