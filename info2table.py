#!/usr/bin/env python3
# vim: syntax=python expandtab
""" 
Read profile cutoffs from TIGRFAM INFO files into a single tab separated file.
"""
__author__ = "Fredrik Boulund"
__date__ = "2017-11-07"

from sys import argv, exit
import argparse


def parse_args():
    desc = "{doc} Copyright {date} {author}.".format(
            doc=__doc__,
            date=__date__,
            author=__author__
            )
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("INFO", nargs="+", 
            help="TIGRFAM INFO files.")
    parser.add_argument("-o", "--output", 
            default="TIGRFAM_INFO.tsv",
            help="Output filename [%(default)s].")

    if len(argv) < 2:
        parser.print_help()
        exit(1)

    return parser.parse_args()


def parse_tigr_info(info_files):
    """Parse TIGR accession and relevant cutoffs from TIGR INFO files.
    """
    for info_file in info_files:
        with open(info_file) as f:
            accession, trusted_global, trusted_domain, noise_global, noise_domain = info_file, 0, 0, 0, 0
            try:
                for line in f:
                    if line.startswith("AC"):
                        accession = line.strip().split()[1]
                    elif line.startswith("TC"):
                        trusted_global, trusted_domain = line.strip().split()[1:]
                    elif line.startswith("NC"):
                        noise_global, noise_domain = line.strip().split()[1:]
            except UnicodeDecodeError:
                print("ERROR, can't read:", info_file)
            yield accession, trusted_global, trusted_domain, noise_global, noise_domain


def create_table(outfile, info_tuples):
    """Create tsv output for all info_tuples.
    """

    out_str = "{}\t{}\t{}\t{}\t{}\n"
    with open(outfile, 'w') as out:
        out.write(out_str.format("accession",
                                 "trusted_global",
                                 "trusted_domain",
                                 "noise_global", 
                                 "noise_domain"))
        for info in info_tuples:
            out.write(out_str.format(*info))


if __name__ == "__main__":
    args = parse_args()
    info_tuples = parse_tigr_info(args.INFO)
    create_table(args.output, info_tuples)
