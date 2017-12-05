# TIGRFAM scripts
Small utility scripts to make working with TIGRFAMs a bit more convenient.
The main scripts are `download_tigrfam_annotations.py` and
`count_tigrfam_annotations.py`. 

## Download TIGRFAM annotations
The `download_tigrfam_annotations.py` script accesses TIGRFAM annotations via
the JCVI web API, and downloads these in tab separated text (`.tsv`). Example usage:

    ./download_tigrfam_annotations.py --workers 10 --output TIGRFAM_annotations.tsv

This will make requests to the web API using 10 parallel workers, and write the
output to `TIGRFAM_annotations.tsv`. The order of the output is random due to
the parallel workers. If you _really_ need to have the table sorted, it's easy
to just run the output file into GNU `sort` afterwards.

It is also possible to download annotations for a subset of TIGRFAMs using the
`--start` and `--end` arguments.  The script will then download information for
all TIGRFAMS in the range from `--start` to `--end`.

## Count TIGRFAM annotations
The `count_tigrfam_annotations.py` scripts parses `hmmsearch` table output
files (`--tblout`) to count the number of sequences/reads that match to each
TIGRFAM, using the cutoffs given by the TIGRFAM annotations (as can be
downloaded using the download script, see above). 


# Deprecated
There is a script called `info2table.py` that produces a tab separated table
from TIGRFAM INFO files (usually downloaded from the TIGRFAM FTP server in a
tarball, e.g. `TIGRFAMs_15.0_INFO.tar.gz`). This isn't very useful anymore,
since the `download_tigrfam_annotations.py` script produces more annotation
information. It seems the data in the INFO files isn't kept up to date any
more.

Another script is called `create_tigrfam_hierarchy.py`, which produces a tab
separated table of the TIGRFAM, MAINROLE, and SUB1ROLE information available in
the `TIGR_ROLE_NAMES` and `TIGR_ROLE_LINK` files, also usually downloaded from
the TIGRFAM FTP.  It appears these files are no longer kept up to date.

# Contribue
Feel free to contribue with pull requests if you see errors or things that need
improvement.
