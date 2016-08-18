
import bisect
import collections
import html
import itertools
import mosestokenizer
import openfile
import operator
import sys


_phrase_table_cache = dict()
# _phrase_table_cache[filename] => (phrases, weigths, maxn)


class BilingualCoverage:

    def __init__(self, filename, langs, simpler=False):
        self.filename = filename
        self.langs = list(langs)
        self.simpler = simpler
        assert len(self.langs) == 2
        self.tokenizers = [
            mosestokenizer.MosesTokenizer(lang, old_version=True)
            for lang in self.langs
        ]
        self.scores = []
        try:
            self.init_from_cache()
        except:
            self.load_phrase_table()
            self.save_to_cache()

    def __str__(self):
        tpl = "BilingualCoverage(filename={filename}, langs={langs})"
        return tpl.format(**vars(self))

    def load_phrase_table(self):
        print("Loading", self.filename, file=sys.stderr)
        self.phrases = (collections.defaultdict(list),
                        collections.defaultdict(list))
        self.weights = []
        self.maxn = [0, 0]
        with openfile.openfile(self.filename) as lines:
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                columns = line.split("|||")
                if len(columns) >= 2:
                    entryid = len(self.weights)
                    nchars = []
                    for side in 0, 1:
                        phrase = html.unescape(columns[side]).lower()
                        tokens = self.tokenizers[side](phrase)
                        nchars.append(sum(map(len, tokens)))
                        ntokens = len(tokens)
                        phrase = " ".join(tokens)
                        if ntokens > self.maxn[side]:
                            self.maxn[side] = ntokens
                        self.phrases[side][phrase].append(entryid)
                    weight = nchars[0] * nchars[1]
                    self.weights.append(weight)
        print("Loaded", len(self.weights), "entries;",
              "maxn1={}; maxn2={}".format(*self.maxn), file=sys.stderr)

    def init_from_cache(self):
        self.phrases, self.weights, self.maxn = \
            _phrase_table_cache[self.filename]
        print("Reusing cached phrase table:", self.filename, file=sys.stderr)

    def save_to_cache(self):
        _phrase_table_cache[self.filename] = \
            self.phrases, self.weights, self.maxn

    def find_phrases(self, tokens, side):
        found = collections.defaultdict(list)
        for n in range(1, self.maxn[side]+1):
            for start in range(len(tokens)-n+1):
                end = start + n
                phrase = " ".join(tokens[start:end])
                if phrase in self.phrases[side]:
                    for entryid in self.phrases[side][phrase]:
                        found[entryid].append((start, end))
        return found

    def gen_phrase_cands(self, tokens1, tokens2):
        found1 = self.find_phrases(tokens1, 0)
        found2 = self.find_phrases(tokens2, 1)
        candidates = []
        for entryid in set(found1).intersection(set(found2)):
            occs1 = found1[entryid]
            occs2 = found2[entryid]
            cartesian_prod = itertools.product(occs1, occs2)
            for (start1, end1), (start2, end2) in cartesian_prod:
                weight = self.weights[entryid]
                candidates.append((start1, end1, start2, end2, weight))
        return candidates

    def score(self, sentence1, sentence2):
        tokens1 = self.tokenizers[0](sentence1.lower())
        tokens2 = self.tokenizers[1](sentence2.lower())
        if len(tokens1) == 0 or len(tokens2) == 0:
            return 0.0
        candidates = self.gen_phrase_cands(tokens1, tokens2)
        candidates = self.greedy_cand_selection(candidates)
        score = self.coverage_analysis(candidates, tokens1, tokens2)
        self.scores.append(score)
        return score

    def greedy_cand_selection(self, candidates):
        get_weigth = operator.itemgetter(4)
        # sort by decreasing weigth
        candidates = sorted(candidates, key=get_weigth, reverse=True)
        covered1 = collections.defaultdict(list)
        covered2 = collections.defaultdict(list)
        selected = []
        for cand in candidates:
            overlapping = set()
            for pos1 in self.cand_range(cand, 0):
                if pos1 in covered1:
                    overlapping.update(covered1[pos1])
            for pos2 in self.cand_range(cand, 0):
                if pos2 in covered2:
                    overlapping.update(covered2[pos2])
            compatible = all(self.is_compatible(cand, other)
                             for other in overlapping)
            if compatible:
                selected.append(cand)
                for pos1 in self.cand_range(cand, 0):
                    covered1[pos1].append(cand)
                for pos2 in self.cand_range(cand, 1):
                    covered2[pos2].append(cand)
        return selected

    def is_compatible(self, cand_a, cand_b):
        range1_a = set(self.cand_range(cand_a, 0))
        range1_b = set(self.cand_range(cand_b, 0))
        range2_a = set(self.cand_range(cand_a, 1))
        range2_b = set(self.cand_range(cand_b, 1))

        intersect_1 = range1_a.intersection(range1_b)
        intersect_2 = range2_a.intersection(range2_b)
        if not intersect_1 and not intersect_2:
            return True
        if intersect_1 and intersect_2:
            return True
        return False

    def cand_range(self, cand, side):
        start1, end1, start2, end2, weight = cand
        if side == 0:
            return range(start1, end1)
        else:
            return range(start2, end2)

    def coverage_analysis(self, candidates, tokens1, tokens2):
        covered1 = set()
        covered2 = set()
        for start1, end1, start2, end2, weight in candidates:
            covered1.update(range(start1, end1))
            covered2.update(range(start2, end2))
        if not covered1 or not covered2:
            return 0
        coverage1 = sum(len(token) for pos, token in enumerate(tokens1)
                        if pos in covered1)
        coverage1 /= sum(len(token) for token in tokens1)
        coverage2 = sum(len(token) for pos, token in enumerate(tokens2)
                        if pos in covered2)
        coverage2 /= sum(len(token) for token in tokens2)
        return coverage1 * coverage2

    def __del__(self):
        self.scores.sort()
        prev_n = 0
        print("scores_dist:", file=sys.stderr)
        for score in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            n = bisect.bisect_right(self.scores, score, lo=prev_n)
            print(score, n, n - prev_n, sep="\t", file=sys.stderr)
            prev_n = n
