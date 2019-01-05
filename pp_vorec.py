#!/usr/bin/env python3
import sys
import re
import random
import Stemmer
from collections import defaultdict
from collections import namedtuple

from markov import MarkovChain
import text_util as Text
from ptr_natal import natal_ptr_words_list


def text_from_words_list(words):
    return ' '.join(map(str, words))


def generate_words_list(src_text, chars_max_count=0, words_max_count=0):
    if chars_max_count <= 0 and words_max_count <= 0:
        raise ValueError('Either chars_max_count or words_max_count must be positive.')
    
    output_words = []
    src_text = src_text.lower()
    cleared_text = Text.clear_input_text(src_text)

    words = Text.split_text_alnum(cleared_text)
    punct_words = Text.split_text_punct(cleared_text)

    chain = MarkovChain()
    for i in range(1, len(words)):
        chain.add_pair(words[i - 1].root, words[i])

    punct_chain = MarkovChain()
    for i in range(len(punct_words) - 1):
        if not Text.is_punct(punct_words[i]):
            if Text.is_punct(punct_words[i + 1]):
                punct_chain.add_pair(punct_words[i].root, punct_words[i + 1].root)
            else:
                punct_chain.add_pair(punct_words[i].root, '')

    suffix_chain = MarkovChain()  # (previous suffix, current root) -> current suffix
    for i in range(1, len(words)):
        suffix_chain.add_pair((words[i - 1].suffix, words[i].root), words[i].suffix)

    next_word, prev_word = Text.Word(''), Text.Word('')
    generated_chars = 0

    while True:
        prev_word = next_word
        if next_word.is_empty():
            next_word = random.choice(words)
        else:
            next_word = chain.get_next_word(next_word.root, lambda: Text.Word(''))

        suffix = suffix_chain.get_next_word((prev_word.suffix, next_word.root), lambda: '')
        if len(suffix) == 0:
            suffix = next_word.suffix

        punct = punct_chain.get_next_word(next_word.root, lambda: '')

        if len(output_words) == 0 or output_words[-1].is_ending_word():
            res_word = Text.PunctedWord(next_word.root.capitalize(), suffix, punct)
        else:
            res_word = Text.PunctedWord(next_word.root, suffix, punct)

        output_words += [res_word] 
        generated_chars += len(res_word)
        if chars_max_count > 0 and generated_chars > chars_max_count:
            break
        if words_max_count > 0 and len(output_words) > words_max_count:
            break
    
    output_words[-1].punct = '.'
    return output_words


def generate_text(src_text, chars_max_count=0, words_max_count=0):
    return text_from_words_list(natal_ptr_words_list(generate_words_list(src_text, chars_max_count, words_max_count)))


def main():
    input_filename = 'input.txt'
    output_filename = 'output.txt'

    if len(sys.argv) > 1 and sys.argv[1] == '--usage':
        print('Usage: python {0} <input file> <output file>'.format(sys.argv[0]))
        sys.exit()

    if len(sys.argv) == 3:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]

    with open(input_filename, 'r', encoding='utf-8') as f:
        text = f.read()

    words = natal_ptr_words_list(generate_words_list(text, words_max_count=1000))
    text = text_from_words_list(words)

    print(text)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    main()
