# coding: utf8
from collections import Counter
from itertools import permutations
from re import sub
from math import log2
from time import time

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщьыэюя'
MOST_FREQUENTLY_BIGRAMS = ('ст', 'но', 'то', 'на', 'ен')


def open_text(filename):
    with open(filename, 'r') as file:
        text_str = file.read()

    return sub('\n', '', text_str)


def save_text(filename, string):
    with open(filename, 'w') as file:
        file.write(string)


def get_bigrams_frequency(string, step=1, sort=True):
    f_dict = {}

    for i in range(0, len(string) - 1, step):
        if string[i] + string[i + 1] in f_dict:
            f_dict[string[i] + string[i + 1]] += 1
        else:
            f_dict[string[i] + string[i + 1]] = 1

    if not sort:
        return f_dict

    return sorted(f_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)


def gcd(b, n):
    """
    Extended euclidean algorithm

    :param b: int
    :param n: int
    :return: greatest common divisor, x from equation ax + by = GCD
    """

    x0, x1 = 1, 0

    while n:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1

    return b, x0


def get_inverse(a, b):
    """
    :param a: int
    :param b: int
    :return: GCD, inverse element to a modulo b (if exist) or None
    """

    d, x = gcd(a, b)

    if d == 1:
        return d, x % b

    return d, None


def get_entropy(f_list, power, n=1):
    return -sum({i: f_list[i] / power * log2(f_list[i] / power) for i in f_list}.values()) / n


def solve_linear_comparison(a, b, m):
    """
    Solve linear comparison (find x):
    ax = b(mod m)

    :param a: int
    :param b: int
    :param m: int
    :return: list of int or None
    """

    d, a_inv = get_inverse(a, m)

    if a_inv:
        return [(a_inv * b) % m]

    elif not b % d:
        a, b, m = a / d, b / d, m / d
        x0 = (b * get_inverse(a, m)[1]) % m
        return [int(x0 + (i - 1) * m) for i in range(1, d + 1)]


def get_key1(x1, x2, y1, y2):
    """
    Find the first key element (key1, key2)

    :param x1: str
    :param x2: str
    :param y1: str
    :param y2: str
    :return: list of int or None
    """

    x1 = ALPHABET.index(x1[0]) * len(ALPHABET) + ALPHABET.index(x1[1])
    x2 = ALPHABET.index(x2[0]) * len(ALPHABET) + ALPHABET.index(x2[1])

    y1 = ALPHABET.index(y1[0]) * len(ALPHABET) + ALPHABET.index(y1[1])
    y2 = ALPHABET.index(y2[0]) * len(ALPHABET) + ALPHABET.index(y2[1])

    results = solve_linear_comparison(y1 - y2, x1 - x2, len(ALPHABET) ** 2)

    if results is not None:
        return [x for x in [get_inverse(i, len(ALPHABET) ** 2)[1] for i in results] if x is not None]


def get_key2(x1, y1, a):
    """
    Find second key element (key1, key2)

    :param x1: str
    :param y1: str
    :param a: result of get_key1(), not None
    :return: int, < len(ALPHABET)^2
    """

    x1 = ALPHABET.index(x1[0]) * len(ALPHABET) + ALPHABET.index(x1[1])
    y1 = ALPHABET.index(y1[0]) * len(ALPHABET) + ALPHABET.index(y1[1])

    return (y1 - a * x1) % len(ALPHABET) ** 2


def check_text_correctness(f_list_s, f_list_big, text_len):
    """
    Check text correctness using entropic criterion

    :param f_list_s: dictionary frequencies of symbols in the text
    :param f_list_big: dictionary frequencies of bigrams in the text
    :param text_len: text length
    :return: bool
    """

    return get_entropy(f_list_s, text_len) < 4.5 and get_entropy(f_list_big, text_len, n=2) < 4.2


def decrypt_from_affinity_sub(string, key):
    """
    Decrypt text with a certain key

    :param string: CT (str)
    :param key: (key1, key2)
    :return: OT (str)
    """

    new_str = ''

    for i in range(0, len(string), 2):
        y = ALPHABET.index(string[i]) * len(ALPHABET) + ALPHABET.index(string[i + 1])
        x = (get_inverse(key[0], len(ALPHABET) ** 2)[1] * (y - key[1])) % len(ALPHABET) ** 2
        new_str += ALPHABET[x // len(ALPHABET)] + ALPHABET[x % len(ALPHABET)]

    return new_str


def gnc_keys(string, f_size=5, check_bw=False):
    """
    Generate and check keys

    :param string: CT (str)
    :param f_size: number of frequently used bigrams of CT, which will generate the keys
    :param check_bw: ask whether to save the text which passed the test (bool)
    :return: None
    """

    f_list = get_bigrams_frequency(string)[:f_size]

    for i in permutations(MOST_FREQUENTLY_BIGRAMS, 2):
        for j in range(len(f_list) - 1):
            key_1 = get_key1(i[0], i[1], f_list[j][0], f_list[j + 1][0])

            if key_1 is None:
                continue

            for solution in key_1:
                key = (solution, get_key2(i[0], f_list[j][0], solution))
                d_text = decrypt_from_affinity_sub(string, key)

                if check_text_correctness(Counter(d_text), get_bigrams_frequency(d_text, sort=False), len(d_text)):
                    if check_bw:
                        print(d_text[:40])
                        answer = input('Save text (yes/no)? ')
                    else:
                        answer = 'yes'

                    if answer == 'yes':
                        save_text('text_decrypted.in', d_text)
                        print('Key =', key)
                        return

if __name__ == '__main__':
    start = time()
    cipher_text = open_text('text_for_dec.in')
    gnc_keys(cipher_text, check_bw=True)
    print('Work time:', round(time() - start, 5), 's')
