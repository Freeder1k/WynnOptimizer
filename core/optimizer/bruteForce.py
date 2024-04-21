import itertools
from typing import TypeVar, Generator

T = TypeVar('T')


def generate_all_permutations(n: int, *choices: T, repeat=False, ordered=False) -> Generator[tuple[T], None, None]:
    """
    Generate all permutations of length n of the given choices.
    :param n: The length of the permutation.
    :param choices: The choices to generate the permutations from.
    :param repeat: Whether to allow the same element multiple times in the permutation.
    :param ordered: Whether to preserve order.
    :return: A generator yielding all permutations of length n of the given choices.
    """
    if len(choices) == 0:
        return  # Don't yield since the result would be shorter than the requested n
    if n == 1:
        for choice in choices:
            yield (choice,)
    else:
        for i in range(len(choices)):
            for sub_choice in generate_all_permutations(n - 1,
                                                        *(choices[:i] if not ordered else ()),
                                                        *choices[i if repeat else i + 1:],
                                                        repeat=repeat,
                                                        ordered=ordered):
                yield (choices[i],) + sub_choice


def generate_all_subpermutations(*choices: T, repeat: bool = False, ordered: bool = False) -> Generator[
    tuple[T], None, None]:
    """
    Generate all sub permutations of the given choices. A sub-permutation u of a set U fulfills: u ⊂ U.
    Does not return an empty tuple.
    :param choices: The choices to generate the sub-permutations from.
    :param repeat: Whether to allow the same element multiple times in the sub-permutation.
    :param ordered: Whether to preserve order.
    :return: A generator yielding all sub-permutations of the given choices.
    """
    for i in range(1, len(choices)):
        for choice in generate_all_permutations(i, *choices, repeat=repeat, ordered=ordered):
            yield choice


def gen_permutations_fast(n: int, *choices: str, repeat: bool = False, ordered: bool = False):
    """
    Generate all permutations of length n of the given choices. (Compiles with jit).
    :param n: The length of the permutation.
    :param choices: The choices to generate the permutations from.
    :param repeat: Whether to allow the same element multiple times in the permutation.
    :param ordered: Whether to preserve order.
    :return: A generator yielding all permutations of length n of the given choices.
    """
    if repeat and not ordered:
        return itertools.product(choices, repeat=n)
    if not repeat and not ordered:
        return itertools.permutations(choices, n)
    if not repeat and ordered:
        return itertools.combinations(choices, n)
    if repeat and ordered:
        return itertools.combinations_with_replacement(choices, n)
