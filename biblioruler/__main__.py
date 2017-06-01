# biblioruler main file

import traceback
import argparse
import logging
import sys
import os
import os.path as op
from importlib import import_module
import sqlite3

# --- Utility functions

def configure_manager(prefix, name, args):
    print("Configuring manager %s" % name)
    m = import_module("biblioruler.managers.%s" % name)
    return m.Manager.create(prefix, args)

def configure_exporter(prefix, name, args):
    print("Configuring exporter %s" % name)
    m = import_module("biblioruler.exporters.%s" % name)
    return m.Exporter.create(prefix, args)

# --- Commands

def command_sync(args, remaining_args):
    assert source != target
    source, remaining_args = configure_manager("source-", args.source, remaining_args)
    pass

def command_export(args, remaining_args):
    source, remaining_args = configure_manager("source-", args.source, remaining_args)
    exporter, remaining_args = configure_exporter("exporter-", args.exporter, remaining_args)

    exporter.export(args.path, source.publications(), source.collections().values())


# --- Parse command line arguments

parser = argparse.ArgumentParser(description='Process bibliographic information.')
parser.add_argument("--debug", action='store_true', default=False, help="Print debug information")
parser.add_argument("--config", action='store_true', default=op.expanduser("~/.biblioruler"), help="Print debug information")

subparsers = parser.add_subparsers(help='Command', dest='command')

parser_sync = subparsers.add_parser('sync', help='Synchronize two accounts')
parser_sync.add_argument("source",)
parser_sync.add_argument("destination")


parser_export = subparsers.add_parser('export', help='Export')
parser_export.add_argument("source")
parser_export.add_argument("exporter")
parser_export.add_argument("path", help="The output path (without extension) - this can be either a folder or a file, depending on the exporter")

args, remaining_args = parser.parse_known_args()
if args.command is None:
    sys.stderr.write("No command given.\n\n")
    parser.print_usage()
    sys.exit(1)

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)


if not op.exists(args.config):
    logging.info("Creating configuration directory")
    os.mkdir(args.config)

db = sqlite3.connect(op.join(args.config, "data.db"))

try:
    logging.debug("Calling command %s" % args.command)
    fname = "command_%s" % args.command.replace("-", "_")
    locals()[fname](args, remaining_args)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    sys.exit(1)
