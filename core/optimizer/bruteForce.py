from typing import TypeVar, Generator, Tuple

T = TypeVar('T')

def generate_all_combinations(n: int, *choices: T) -> Generator[Tuple[T], None, None]:
    if n == 1:
        for choice in choices:
            yield (choice,)
    else:
        for sub_combination in generate_all_combinations(n - 1, *choices):
            for choice in choices:
                yield (choice,) + sub_combination