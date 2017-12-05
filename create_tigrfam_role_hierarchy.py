#!/usr/bin/env python3
# vim: syntax=python expandtab
""" 
Read TIGRFAM role names and role links to construct a hierarchical index of TIGRFAMs.
"""
__author__ = "Fredrik Boulund"
__date__ = "2017-11-14"

from sys import argv, exit
from collections import defaultdict
import argparse


def parse_args():
    
    desc = "{doc} Copyright {date} {author}.".format(
            doc=__doc__,
            date=__date__,
            author=__author__
            )
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-n", "--role-names", dest="role_names", required=True,
            help="Path to TIGR_ROLE_NAMES.")
    parser.add_argument("-l", "--role-links", dest="role_links", required=True,
            help="Path to TIGRFAMS_ROLE_LINK.")
    parser.add_argument("-o", "--output", 
            default="TIGRFAM_hierarchy.tsv",
            help="Output filename [%(default)s].")

    if len(argv) < 2:
        parser.print_help()
        exit(1)

    return parser.parse_args()


def parse_role_names(role_names_filename):
    """
    Parse TIGRFAM_ROLE_NAMES.
    """
    role_descriptions = defaultdict(dict)
    with open(role_names_filename) as f:
        for line in f:
            _, role_id, rank, role_desc = line.strip().split(maxsplit=3)
            role_descriptions[role_id][rank[:-1]] = role_desc
    return role_descriptions


def parse_role_links(role_links_filename):
    """
    Parse TIGRFAMS_ROLE_LINK.
    """
    tigrfam_role = {}
    with open(role_links_filename) as f:
        for line in f:
            tigrfam, role = line.strip().split()
            tigrfam_role[tigrfam] = role
    return tigrfam_role


if __name__ == "__main__":
    args = parse_args()

    role_descriptions = parse_role_names(args.role_names)
    tigrfam_role = parse_role_links(args.role_links)

    out_str = "{}\t{}\t{}\n"
    with open(args.output, 'w') as outfile:
        outfile.write(out_str.format("MAINROLE", "SUB1ROLE", "TIGRFAM"))
        for tigrfam, role_id in tigrfam_role.items():
            try:
                outfile.write(out_str.format(role_descriptions[role_id]["mainrole"],
                        role_descriptions[role_id]["sub1role"],
                        tigrfam))
            except KeyError:
                outfile.write(out_str.format("NA", "NA", tigrfam))
