#!/usr/bin/env python3
import re
import random
from collections import defaultdict
from collections import namedtuple

import text_util as Text

class _MarkovToken:
    __slots__ = ('word', 'count')
    def __init__(self, word, count=0):
        self.word = word
        self.count = count

    def __str__(self):
        return '{} ({})'.format(self.word.__str__(), self.count)

    def __repr__(self):
        return 'MarkovToken({}, {})'.format(self.word.__repr__(), self.count)


class _MarkovPairs:
    __slots__ = ('pairs', 'total_count', 'probabilities')
    def __init__(self):
        self.pairs = []
        self.probabilities = ()
        self.total_count = 0
    
    def __str__(self):
            return self.pairs.__str__()
    
    def __repr__(self):
        return self.pairs.__repr__()
    
    def get_count(self, word):
        pair_idx = self._get_pair_idx(word)
        if pair_idx is not None:
            return self.pairs[pair_idx].count
        else:
            return 0

    def inc_count(self, word):
        self.total_count += 1

        pair_idx = self._get_pair_idx(word)
        if pair_idx is not None:
            self.pairs[pair_idx].count += 1
        else:
            self.pairs.append(_MarkovToken(word=word, count=1))

        self._rebuild_probabilities()

    def get_next_word(self, chain_end_func):
        if len(self.pairs) == 0:
            return chain_end_func()
        
        idx = self._prob_choice()
        if idx < 0 or idx >= len(self.pairs):
            return chain_end_func()
        else:
            return self.pairs[idx].word

    def _prob_choice(self):
        num = random.random()
        idx = 0
        interval = (0, self.probabilities[idx])
        while num < interval[0] or num >= interval[1]:
            idx += 1
            interval = (interval[1], interval[1] + self.probabilities[idx])
        return idx

    def _rebuild_probabilities(self):
        self.probabilities = tuple(x.count / self.total_count for x in self.pairs)

    def _get_pair_idx(self, word):
        for i in range(len(self.pairs)):
            if self.pairs[i].word == word:
                return i
        return None


class MarkovChain:
    def __init__(self):
        self.sources = defaultdict(lambda: _MarkovPairs())

    def __repr__(self):
        return 'MarkovChain({})'.format(dict.__repr__(self.sources))

    def add_pair(self, word_from, word_to):
        self.sources[word_from].inc_count(word_to)
        return self

    def convert_words_list(self, words):
        for i in range(len(words) - 1):
            self.add_pair(words[i], words[i + 1])
        return self
        
    def get_next_word(self, source_word, chain_end_func):
        token = self.sources[source_word]
        return token.get_next_word(chain_end_func)
