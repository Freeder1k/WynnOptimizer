from typing import TypeVar

T = TypeVar('T')

def generate_all_combinations(n: int, *choices: T):
    if n == 1:
        for choice in choices:
            yield (choice,)
    else:
        for sub_combination in generate_all_combinations(n - 1, *choices):
            for choice in choices:
                yield (choice,) + sub_combination