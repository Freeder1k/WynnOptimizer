from typing import TypeVar, Generator

T = TypeVar('T')


def generate_all_permutations(n: int, *choices: T, repeat=False, ordered=False) -> Generator[tuple[T], None, None]:
    if n == 1:
        for choice in choices:
            yield (choice,)
    else:
        if len(choices) == 0:
            return  # Don't yield since the result would be shorter than the requested n
        for i in range(len(choices)):
            for sub_choice in generate_all_permutations(n - 1, *(choices[:i] if not ordered else ()),
                                                        *choices[i if repeat else i + 1:], repeat=repeat,
                                                        ordered=ordered):
                yield (choices[i],) + sub_choice


def generate_all_subpermutations(*choices: T, repeat: bool = False, ordered: bool = False) -> Generator[
    tuple[T], None, None]:
    for i in range(1, len(choices) + 1):
        for choice in generate_all_permutations(i, *choices, repeat=repeat, ordered=ordered):
            yield choice
