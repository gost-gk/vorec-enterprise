#!/usr/bin/env python3
import re
import Stemmer

from typing import Union

_PUNCTUATION = set(',.…!-—:;')
_STEMMER = Stemmer.Stemmer('russian')

class Word:
    __slots__ = ('root', 'suffix')
    def __init__(self, root, suffix: str=''):
        self.root = str(root)
        self.suffix = suffix

    def __repr__(self):
        return 'Word(\'{}\', \'{}\')'.format(self.root, self.suffix)

    def __str__(self):
        return self.root + self.suffix

    def __len__(self):
        return len(self.root) + len(self.suffix)

    def __eq__(self, value):
        if isinstance(value, Word):
            return self.root == value.root and self.suffix == value.suffix
        else:
            return str(self) == str(value)

    def __hash__(self):
        return str(self).__hash__()

    def lower(self):
        return Word(self.root.lower(), self.suffix.lower())

    def is_empty(self):
        return len(self.root) == 0

    def is_punct(self):
        return len(self.suffix) == 0 and is_punct(self.root)


class PunctedWord(Word):
    __slots__ = ('root', 'suffix', 'punct')
    def __init__(self, root, suffix, punct):
        super().__init__(root, suffix=suffix)
        self.punct = punct
    
    def __repr__(self):
        return "PunctedWord('{}' '{}' '{}')".format(self.root, self.suffix, self.punct)

    def __str__(self):
        return '{}{}{}'.format(self.root, self.suffix, self.punct)

    def __len__(self):
        return super().__len__() + len(self.punct)

    def is_ending_word(self):
        return len(self.punct) > 0 and self.punct in '.!?'


def is_punct(word):
    if isinstance(word, Word):
        return word.is_punct()
    else:
        return word in _PUNCTUATION
    

def stem_word(word: str):
    stemmed_word = _STEMMER.stemWord(word)
    return Word(stemmed_word, word[len(stemmed_word):])


def fix_multiple_spaces(text: str):
    return re.sub(r'(\s+)', ' ', text)


def clear_input_text(text: str):
    return fix_multiple_spaces(text.replace('\n', ' ').replace('\r', ' '))


def split_text_alnum(text: str):
    text = re.sub(r'\s\-([\w\d])', r' \1', text)
    text = re.sub(r'([\w\d])\- ', r'\1 ', text)
    text = fix_multiple_spaces(re.sub(r'[^\w\d\- ]', '', text))
    return list(map(stem_word, text.split(' ')))


 # rww: special case for 'по-русски' and so on
def _is_hyphen_part_of_word(text: str, i: int):
        return i > 0 and i < len(text) - 1 and text[i - 1].isalnum() and text[i + 1].isalnum()
        

def split_text_punct(text: str):
    filtered_list = []
    for i in range(len(text)):
        x = text[i]
        if x.isalnum() or x == ' ' or (x == '-' and _is_hyphen_part_of_word(text, i)):
            filtered_list += [x]
        elif x in _PUNCTUATION:
            filtered_list += [' ' + x + ' ']
    return list(map(stem_word, fix_multiple_spaces(''.join(filtered_list)).split(' ')))
