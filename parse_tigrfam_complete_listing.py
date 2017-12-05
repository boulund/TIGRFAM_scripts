#!/usr/bin/env python3
# vim: syntax=python expandtab
"""
Parse TIGRFAM complete listing HTML table.
"""
__author__ = "Fredrik Boulund"
__date__ = "2017-12-05"

from sys import argv, exit
import argparse
import urllib.request
from bs4 import BeautifulSoup as bs


def parse_args():
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-w", "--webpage", 
            default="http://www.jcvi.org/cgi-bin/tigrfams/Listing.cgi",
            help="JCVI TIGRFAMs complete listing webpage [%(default)s].")
    parser.add_argument("-o", "--output", required=True,
            default="TIGRFAM_complete_listing.tsv",
            help="Output filename [%(default)s].")

    if len(argv) < 2:
        parser.print_help()
        exit(1)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    with open(args.output, 'w') as outfile, urllib.request.urlopen(args.webpage) as response:
        soup = bs(response.read(), "lxml")
        rows = soup.find("table").findAll("tr")
        format_str = "{}\t{}\t{}\t{}\t{}"
        for idx, row in enumerate(rows):
            if idx > 0:
                columns = [cell.text for cell in row.findAll("td")]
            else:
                columns = [cell.text for cell in row.findAll("th")]
            print(format_str.format(*columns), file=outfile)
