lrec2016sentalign
=================

This is the first draft of a phrase-table-based sentence alignment tool. This
software is based on Bleualign and only changes the scoring function.  See
README_bleualign.md for further information regarding the original Bleualign.

This implementation allows exact reproduction of the results presented in the
LREC 2016 paper listed below in section PUBLICATIONS.

Copyright ⓒ 2016
Luís Gomes <luismsgomes@gmail.com>

Copyright ⓒ 2010
Rico Sennrich <sennrich@cl.uzh.ch>

Project Homepage: http://github.com/luismsgomes/lrec2016sentalign
Bleualign Project Homepage: http://github.com/rsennrich/bleualign

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation


GENERAL INFO
------------

Bleualign is a tool to align parallel texts (i.e. a text and its translation)
on a sentence level.
Additionally to the source and target text, this modified version of Bleualign
requires a bilingual phrase table such as those produced by the Moses toolkit.
Another tool for producing phrase tables is Anymalign.

The alignment is performed on the basis of the ratio of characters
from the source and target sentences that are covered by bilingual phrases
found in the given table.
See section PUBLICATIONS for more details.

Obtaining a bilingual phrase table is up to the user, but we recommend using
the Moses toolkit.


REQUIREMENTS
------------

The software was developed on Linux using Python 3.X.
There are a couple of required Python modules listed in requirements.txt.
They are easily installable with pip:

    pip3 install -r requirements.txt



INSTRUCTIONS FOR REPRODUCING THE RESULTS OF THE PAPER
-----------------------------------------------------

For reproducing the evaluation presented in the paper you just need to execute
the script compare-metrics.sh.  Note that the evaluation results are cached in
directory "results".  If you want to rerun the alignments just change the
variables defined at the top of the script compare-metrics.sh:

    rerun_galechurch=true
    rerun_bleu=true
    rerun_coverage=true


GENERAL USAGE INSTRUCTIONS
--------------------------

The input and output formats of Bleualign are one sentence per line.
A line which only contains .EOA is considered a hard delimiter (end of
article).
Sentence alignment does not cross these delimiters: reliable delimiters
improve speed and performance, wrong ones will seriously degrade performance.

Given the files sourcetext.txt and targettext.txt, a sample call is

    ./bleualign.py -s sourcetext.txt -t targettext.txt \
        --srctotarget - \
        --coverage "table=phrase_tables/table.en-fr langs=en-fr" \
        -o outputfile

    ./bleualign.py -h will show more usage options


BUGS
----

This code is NOT production ready. The modifications that I did to the
original Bleualign should be considered more a quick hack than a
well-engineered solution. In particular, the speed and memory usage are
terrible.  I (ab)used Bleualign as a testbed for experimenting with the new
scoring function and take the "first steps towards coverage-based sentence
alignment".
I don't consider this particular coverage-based scoring function to be the
best coverage-based scoring possible.  You are invited to try your own ;-)

After obtaining the performance improvements reported in the LREC 2016 paper
(see PUBLICATIONS below) I have started working on a new aligner from
scratch, which improves several aspects related to phrase-table matching
speed and memory usage, improved coverage metrics, and improved handling of
large text documents as well as texts extracted from PDF.


PUBLICATIONS
------------

This coverage score employed by this aligner is described in

Luís Gomes, Gabriel Pereira Lopes (2016):
   First Steps Towards Coverage-Based Sentence Alignment.
   In: Proceedings of the LREC 2016, Portoroz, Slovenia.

The original Bleualign algorithm is described in

Rico Sennrich, Martin Volk (2010):
   MT-based Sentence Alignment for OCR-generated Parallel Texts.
   In: Proceedings of AMTA 2010, Denver, Colorado.

Rico Sennrich; Martin Volk (2011):
    Iterative, MT-based sentence alignment of parallel texts.
    In: NODALIDA 2011, Nordic Conference of Computational Linguistics, Riga.


