import enchant
from math import sqrt
from itertools import permutations, chain

import numpy as np

eng_dict = enchant.Dict("en_US")


def check_text(text: str) -> int:
    errors: int = 0
    for word in text.split():
        if not eng_dict.check(word):
            errors += 1
    return errors


def find_mul_pairs(value: int):
    for x in range(2, int(sqrt(value) + 1)):
        if not (value % x):
            yield [x, value // x]


def get_permutation_by_len(permutation_len: int):
    return permutations(range(0, permutation_len), permutation_len)


def perm_text(text: str, permutation: list) -> str:
    permutation: list = list(permutation)
    matrix = np.array(list([char for char in text]))
    text_len: int = len(text)
    width: int = len(permutation)
    height: int = text_len // width
    matrix = matrix.reshape(height, width)
    idx = np.empty_like(permutation)
    idx[permutation] = np.arange(len(permutation))
    matrix[:] = matrix[:, idx]
    return ''.join(np.transpose(matrix).flatten())


def count_max_tries(keyword_lens: list) -> int:
    count: int = 0
    for num in keyword_lens:
        mul: int = 1
        for i in range(1, num + 1):
            mul *= i
        count += mul
    return count


def brute_force(text: str) -> str:
    text_len: int = len(text)
    best_permutation: list = []
    less_error: int = text_len
    keyword_lens: list = sorted(list(chain(*list(find_mul_pairs(text_len)))))
    max_tries: int = count_max_tries(keyword_lens)
    current_try: int = 0
    for keyword_len in keyword_lens:
        for permutation in get_permutation_by_len(keyword_len):
            permed_text: str = perm_text(text, list(permutation))
            errors: int = check_text(permed_text)
            if errors < less_error:
                less_error = errors
                best_permutation = permutation
            yield {
                'permed_text': permed_text,
                'errors': errors,
                'progress': round(current_try * 100 / max_tries) / 100,
                'current_try': current_try
            }
            current_try += 1
    return perm_text(text, best_permutation)


def brute_force_file(filepath: str):
    text: str
    with open(filepath, 'r') as file:
        text: str = ''.join(file.readlines())
    return brute_force(text)
