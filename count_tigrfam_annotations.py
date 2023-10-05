#!/usr/bin/env python3
# vim: syntax=python expandtab
"""
Parse hmmsearch tbl output and use cutoffs from TIGRFAM annotations files to count 
the number of valid assignments.
"""
__author__ = "Fredrik Boulund"
__date__ = "2023-10-05"

from sys import argv, exit
from collections import namedtuple, Counter
import logging
import argparse
import csv

# namedtuple definitions
Cutoffs = namedtuple("model_cutoffs",
        ["accession", "trusted_global", "trusted_domain", "noise_global", "noise_domain"])
Hit = namedtuple("hmmsearch_hit",
        ["target", "t_acc", "q_name", "q_acc", "full_e_value", "full_score",
        "full_bias", "domain_e_value", "domain_score", "domain_bias", "exp",
        "reg", "clu", "ov", "env", "dom", "rep", "inc", "desc"])

def parse_args():
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-t", "--tbl", required=True,
            help="hmmsearch tbl output files.")
    parser.add_argument("-a", "--annotations", required=True,
            help="TIGRFAM annotations (in tab separated format produced by download_tigrfam_annotations.py).")
    parser.add_argument("-o", "--output", 
            default="tigrfam_annotation_counts.tsv",
            help="Output filename [%(default)s].")

    if len(argv) < 2:
        parser.print_help()
        exit(1)

    return parser.parse_args()


def read_tigrfam_cutoffs(annotation_table):
    """
    Parse TIGRFAM model cutoffs from tab separated annotation table produced by
    download_tigrfam_annotations.py.
    """
    model_cutoffs = {} 
    with open(annotation_table) as f:
        annotation_reader = csv.reader(f, delimiter="\t")
        header = next(annotation_reader)
        try:
            for row in annotation_reader:
                accession = row[0]
                trusted_g = row[4]
                trusted_d = row[5]
                noise_g = row[6]
                noise_d = row[7]
                cutoffs_parsed = {"Trusted global": trusted_g, 
                                  "Trusted domain": trusted_d, 
                                  "Noise global": noise_g, 
                                  "Noise domain": noise_d}
                cutoffs_to_insert = []
                for cutoff_name, cutoff in cutoffs_parsed.items():
                    try:
                        cutoffs_to_insert.append(float(cutoff))
                    except ValueError:
                        logging.warning("Couldn't interpret cutoff %14s ('%s') on line %s for %s, defaulting to 1e6.", 
                                cutoff_name, cutoff, annotation_reader.line_num, accession)
                        cutoffs_to_insert.append(1e6)
                model_cutoffs[accession] = Cutoffs(accession, *cutoffs_to_insert)
        except csv.Error as e:
            logging.error("Couldn't parse annotation line %s: %s", annotation_reader.line_num, e)
            exit(2)
    logging.debug("Loaded model cutoffs for %s TIGRFAMs.", len(model_cutoffs))
    return model_cutoffs


def parse_hits(tbl_filename):
    """
    Parse hmmsearch tbl output for hits to TIGRFAMs.
    """
    with open(tbl_filename) as f:
        for line in f:
            if line.startswith("#"):
                continue
            (target, t_acc, q_name, q_acc, 
                    full_e_value, full_score, full_bias, 
                    domain_e_value, domain_score, domain_bias,
                    exp, reg, clu, ov, env, dom, rep, inc, 
                    *desc) = line.strip().split()
            hit = Hit(target, t_acc, q_name, q_acc, 
                    float(full_e_value), float(full_score), float(full_bias),
                    float(domain_e_value), float(domain_score), float(domain_bias),
                    float(exp), int(reg), int(clu), int(ov), int(env),
                    int(dom), int(rep), int(inc), "".join(desc))
            if not hit.q_acc in model_cutoffs:
                logging.debug("Did not find annotation data for %s", hit.target)
                continue
            yield hit
             

def filter_hits(hits):
    for hit in parse_hits(args.tbl):
        if hit.q_name in model_cutoffs:
            yield hit
        else:
            logging.warning(f"{hit} not in model_cutoffs")


if __name__ == "__main__":
    args = parse_args()
    model_cutoffs = read_tigrfam_cutoffs(args.annotations)

    filtered_hits = list(filter(
            lambda hit: hit.domain_score > model_cutoffs[hit.q_name].trusted_domain, 
            filter_hits(parse_hits(args.tbl))))
    tigrfam_counts = Counter(h.q_name for h in filtered_hits)

    with open(args.output, 'w') as outfile:
        outfile.write("TIGRFAM\tcount\n")
        for tigrfam, count in tigrfam_counts.items():
            outfile.write("{}\t{}\n".format(tigrfam, count))

