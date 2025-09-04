import argparse
import sys
from filer.commands import new, root, analyse, dir, check, dedup




def main():
parser = argparse.ArgumentParser(prog="filer", description="File inventory and deduplication tool")
subparsers = parser.add_subparsers(dest="command", required=True)


# new
new.register_parser(subparsers)


# root
root.register_parser(subparsers)


# analyse
analyse.register_parser(subparsers)


# dir
dir.register_parser(subparsers)


# check
check.register_parser(subparsers)


# dedup
dedup.register_parser(subparsers)


args = parser.parse_args()
