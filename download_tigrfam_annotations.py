#!/usr/bin/env python3
# vim: syntax=python expandtab
"""
Download TIGRFAM annotations from JCVI webpage.
"""
__author__ = "Fredrik Boulund"
__date__ = "2017-12-05"

from sys import argv, exit
import argparse
import concurrent.futures
from functools import partial

import requests
from bs4 import BeautifulSoup as bs


def parse_args():
    
    desc = "{doc} Copyright {date} {author}.".format(
            doc=__doc__,
            date=__date__,
            author=__author__
            )
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-a", "--api-endpoint", dest="api_endpoint", metavar="'URL'",
            default="http://www.jcvi.org/cgi-bin/tigrfams/HmmReportPage.cgi?acc=",
            help="JCVI TIGRFAMs HMM report page API access point [%(default)s].")
    parser.add_argument("-s", "--start", metavar="ID",
            default="00001",
            help="Start TIGRFAM ID to download from [%(default)s].")
    parser.add_argument("-e", "--end", metavar="ID",
            default="04571",
            help="End TIGRFAM ID to download to [%(default)s].")
    parser.add_argument("-w", "--workers", metavar="N", type=int,
            default=20,
            help="Number of parallel download workers [%(default)s]")
    parser.add_argument("-o", "--output", required=True,
            default="TIGRFAM_complete_annotations.tsv",
            help="Output filename [%(default)s].")

    if len(argv) < 2:
        parser.print_help()
        exit(1)

    return parser.parse_args()


def sanitize_field(field_text):
    """
    Remove line breaks and other characters that might mess up table.
    """
    strip_chars = ["""""",  # Newline
                   """\n""",  # Newline
                   """	""",  # Tab
                   """""",  # Backspace
                  ]
    sanitized_text = field_text
    for char in strip_chars:
        sanitized_text = sanitized_text.replace(char, " ")
    return sanitized_text


def download_tigrfam_info(tigrfam, api_endpoint):
    """
    Download TIGRFAM from API endpoint.
    """
    return requests.get(api_endpoint+tigrfam).text


def parse_tigrfam_info_table(html_text):
    """
    Parse TIGRFAM info table from API endpoint HTML response.
    """
    soup = bs(html_text, "lxml")
    rows = soup.find("table").findAll("tr")
    columns = {}
    for row in rows:
        key, value = [cell.text for cell in row.findAll("td")]
        nospace_key = key.replace(" ", "_")
        columns[nospace_key] = sanitize_field(value)
    return columns


def validate_entries(data, expected_keys, tigrfam):
    """
    Verify the existence of required keys in TIGRFAM data.
    """
    for expected_key in expected_keys:
        if expected_key in data:
            continue
        else:
            data[expected_key] = ""
    if not data["Accession"]:
        data["Accession"] = tigrfam
    return data


def download_tigrfam_and_parse_data(tigrfam, api_endpoint, expected_keys):
    html_text = download_tigrfam_info(tigrfam, api_endpoint)
    data = parse_tigrfam_info_table(html_text)
    valid_data = validate_entries(data, expected_keys, tigrfam)
    return valid_data


if __name__ == "__main__":
    args = parse_args()

    tigrfams_to_download = ["TIGR{:05d}".format(t) for t in range(int(args.start), int(args.end)+1)]

    format_str = "{Accession}\t{Name}\t{Function}\t{Gene_Symbol}\t{Trusted_Cutoff}\t{Domain_Trusted_Cutoff}\t{Noise_Cutoff}\t{Domain_Noise_Cutoff}\t{Isology_Type}\t{HMM_Length}\t{Mainrole_Category}\t{Subrole_Category}\t{Gene_Ontology_Term}\t{Author}\t{Entry_Date}\t{Last_Modified}\t{Comment}\t{References}\t{Genome_Property}"
    expected_keys = ["Accession", "Name", "Function", "Gene_Symbol", "Trusted_Cutoff", "Domain_Trusted_Cutoff", "Noise_Cutoff", "Domain_Noise_Cutoff", "Isology_Type", "HMM_Length", "Mainrole_Category", "Subrole_Category", "Gene_Ontology_Term", "Author", "Entry_Date", "Last_Modified", "Comment", "References", "Genome_Property"]
    output_table_header = "\t".join(expected_keys)

    downloaded_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download_tigrfam_and_parse_data, tigrfam, args.api_endpoint, expected_keys): tigrfam 
                    for tigrfam in tigrfams_to_download}
        for future in concurrent.futures.as_completed(futures):
            tigrfam = futures[future]
            try:
                downloaded_data.append(future.result())
            except Exception as e:
                print("{} generated an exception: {}".format(tigrfam, e))
    
    with open(args.output, 'w') as outfile:
        print(output_table_header, file=outfile)
        for data in downloaded_data:
            print(format_str.format(**data), file=outfile)


