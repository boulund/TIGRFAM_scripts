#!/usr/bin/env python3
# vim: syntax=python expandtab
"""
Parse hmmsearch tbl output and use cutoffs from TIGRFAM INFO files to count annotations.
"""
__author__ = "Fredrik Boulund"
__date__ = "2017-11-14"

from sys import argv, exit
from collections import namedtuple, Counter
import logging
import argparse

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
    parser.add_argument("-c", "--cutoffs", required=True,
            help="TIGRFAM cutoffs (in five column tab separated format produced by info2table.py).")
    parser.add_argument("-o", "--output", 
            default="tigrfam_annotation_counts.tsv",
            help="Output filename [%(default)s].")

    if len(argv) < 2:
        parser.print_help()
        exit(1)

    return parser.parse_args()


def read_tigrfam_cutoffs(cutoffs_table):
    """
    Parse TIGRFAM model cutoffs from tab separated format produced by info2table.py.
    """
    model_cutoffs = {} 
    with open(cutoffs_table) as f:
        f.readline()  # skip header
        for rownum, line in enumerate(f):
            accession, trusted_g, trusted_d, noise_g, noise_d = line.strip().split("\t")
            try:
                model_cutoffs[accession] = Cutoffs(accession, 
                        float(trusted_g), float(trusted_d), float(noise_g), float(noise_d))
            except ValueError:
                logging.error("Couldn't parse line %s: %s", rownum, line)
                exit(2)
    logging.debug("Read model cutoffs for %s TIGRFAMs.", len(model_cutoffs))
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
            yield hit
             

if __name__ == "__main__":
    args = parse_args()
    model_cutoffs = read_tigrfam_cutoffs(args.cutoffs)

    filtered_hits = list(filter(
            lambda hit: hit.domain_score > model_cutoffs[hit.q_name].trusted_domain, 
            parse_hits(args.tbl)))
    tigrfam_counts = Counter(h.q_name for h in filtered_hits)

    with open(args.output, 'w') as outfile:
        outfile.write("TIGRFAM\tcount\n")
        for tigrfam, count in tigrfam_counts.items():
            outfile.write("{}\t{}\n".format(tigrfam, count))

