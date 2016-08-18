#! /bin/bash

#  CONFIGURATION

rerun_galechurch=false
rerun_bleu=false
rerun_coverage=false

langs="de-fr"
table="phrase_tables/europarl-minfreq5-minscp0001.$langs.xz"

# END OF CONFIGURATION


if $rerun_galechurch || ! test -f results/galechurch_vanilla.txt; then
    echo "running galechurch between source and target"
    ./bleualign.py -e --galechurch --srctotarget - \
        > results/galechurch_vanilla.txt 2>&1
fi

if $rerun_galechurch || ! test -f results/galechurch.txt; then
    echo "running galechurch between translated source and target"
    ./bleualign.py -e --galechurch \
        --srctotarget eval/eval1989.europarlfull.fr \
        > results/galechurch.txt 2>&1
fi

if $rerun_bleu || ! test -f results/bleu_intersected.txt; then
    echo "running bleu-based alignment (intersected)"
    ./bleualign.py -e --srctotarget eval/eval1989.europarlfull.fr \
        --targettosrc eval/eval1989.europarlfull.de \
        > results/bleu_intersected.txt 2>&1
fi

if $rerun_bleu || ! test -f results/bleu.txt; then
    echo "running bleu-based alignment"
    ./bleualign.py -e --srctotarget eval/eval1989.europarlfull.fr \
        > results/bleu.txt 2>&1
fi

if $rerun_bleu || ! test -f results/bleu4.txt; then
    echo "running bleu-based alignment with 4-grams"
    ./bleualign.py -e --srctotarget eval/eval1989.europarlfull.fr \
        --bleu_ngrams 4 > results/bleu4.txt 2>&1
fi

if $rerun_coverage || ! test -f results/coverage.txt; then
    echo "running coverage-based alignment"
    ./bleualign.py -e --coverage "table=$table langs=$langs" \
        > results/coverage.txt 2>&1
fi

grep -rP '^(f1|precision|recall) (strict|lax):' results |
perl -pe 's/^results\/(.*)\.txt:(.*): (.*)$/\1\t\2\t\3/' |
gawk '
function reset_config_scores() {
    config = 0;
    scores["precision strict"] = 0
    scores["recall strict"] = 0
    scores["f1 strict"] = 0
    scores["precision lax"] = 0
    scores["recall lax"] = 0
    scores["f1 lax"] = 0
}
function print_config_scores() {
    print config, \
        scores["precision strict"], \
        scores["recall strict"], \
        scores["f1 strict"], \
        scores["precision lax"], \
        scores["recall lax"], \
        scores["f1 lax"];
}
BEGIN {
    FS="\t";
    OFS="\t";
    reset_config_scores();
}
$1 != config {
    if (config) {
        print_config_scores()
        reset_config_scores();
    }
    config = $1;
    scores[$2] = $3
}
{
    scores[$2] = $3
}
END {
    if (config) {
        print_config_scores();
    }
}
' | sort -t $'\t' -k 4 -r -g |
cat <(echo -e "Metric\tP (strict)\tR (strict)\tF (strict)\tP (lax)\tR (lax)\tF (lax)") - |
column -t -s $'\t'
