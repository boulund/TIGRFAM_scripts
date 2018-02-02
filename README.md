# TIGRFAM scripts
Small utility scripts to make working with TIGRFAMs a bit more convenient.
The main scripts are:

- `download_tigrfam_annotations.py` - Downloads TIGRFAM annotations from JCVI web site
- `count_tigrfam_annotations.py` - Count TIGRFAM matches from `hmmsearch` table output

## Download TIGRFAM annotations
The `download_tigrfam_annotations.py` script accesses TIGRFAM annotations via
the JCVI web API, and downloads these in tab separated text (`.tsv`). Example usage:

    ./download_tigrfam_annotations.py --workers 10 --output TIGRFAM_annotations.tsv

This will make requests to the web API using 10 parallel workers, and write the
output to `TIGRFAM_annotations.tsv`. The order of the output is random due to
the parallel workers. If you _really_ need to have the table sorted, it's easy
to just run the output file into GNU `sort` afterwards. Please don't run this
script with too many workers. Downloading annotations for all TIGRFAMs using
the default setting of 20 workers takes about 5 minutes, the final table is about 4MB.

It is also possible to download annotations for a subset of TIGRFAMs using the
`--start` and `--end` arguments.  The script will then download information for
all TIGRFAMS in the range from `--start` to `--end` (inclusive).

## Count TIGRFAM annotations
The `count_tigrfam_annotations.py` scripts parses `hmmsearch` table output
files (`--tblout`) to count the number of sequences/reads that match to each
TIGRFAM, using the cutoffs given by the TIGRFAM annotations (as can be
downloaded using the download script, see above). 


# Deprecated
There are some old scripts still left in the repo:

- `info2table.py`
- `create_tigrfam_hierarchy.py`

`info2table.py` produces a tab separated table from TIGRFAM INFO files (usually
downloaded from the TIGRFAM FTP server in a tarball, e.g.
`TIGRFAMs_15.0_INFO.tar.gz`). This isn't very useful anymore, since the
`download_tigrfam_annotations.py` script produces more annotation information.
It seems the data in the INFO files isn't kept entirely up to date any more.

`create_tigrfam_hierarchy.py` produces a tab separated table of the TIGRFAM,
MAINROLE, and SUB1ROLE information available in the `TIGR_ROLE_NAMES` and
`TIGR_ROLE_LINK` files, also usually downloaded from the TIGRFAM FTP. This
script is deprecated as it appears these files are no longer kept entirely up
to date, and `download_tigrfam_annotations.py` produces more complete tables.

# Contribute
Feel free to contribute with pull requests if you see errors or things that need
improvement.
