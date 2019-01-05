#!/usr/bin/env
import text_util as Text
from collections import defaultdict

_PTR_BASE = 'указател'

# Замена слов с соответствующим окончанием указателем, экспериментально
_PTRS_SUFFIXES = {
        'ом': 'ем',
        'ем': 'ем',
        'я': 'я',
        'а': 'и',        # мн. ч.
        'ы': 'и',        # мн. ч.
}

# Добавление указателя после предлогов
_PTRS_PREPOSITIONS = {
    'в': 'ь',
    'на': 'ь',
    'об': 'е',
    'по': 'ю',
    'с': 'ем',
    'у': 'я',
    'под': 'ем',
}

def _natal_ptr_preposition(word):
    if len(word.suffix) == 0:
        if word.root in _PTRS_PREPOSITIONS:
            return Text.PunctedWord(_PTR_BASE, _PTRS_PREPOSITIONS[word.root], word.punct)
    else:
        return None

def natal_ptr_words_list(words):
    output_words = [words[0]]
    for i in range(1, len(words) - 1):
        word = words[i]

        if word.suffix in _PTRS_SUFFIXES:  # Замена слова на указатель по окончанию
            word.root = _PTR_BASE if not word.root[0].isupper() else _PTR_BASE.capitalize()
            word.suffix = _PTRS_SUFFIXES[word.suffix]
        else:  # Замена слова на указатель из-за предыдущего предлога
            prep_ptr = _natal_ptr_preposition(words[i - 1]) 
            if prep_ptr is not None:
                word.root = prep_ptr.root
                word.suffix = prep_ptr.suffix
        
        # Комбо из нескольких указателей заменяем цепочкой!
        if output_words[-1].root.lower() == _PTR_BASE and word.root.lower() == _PTR_BASE:
            output_words += [Text.PunctedWord('на', '', '')]

        output_words += [word]

    output_words += [words[-1]]
    return output_words
