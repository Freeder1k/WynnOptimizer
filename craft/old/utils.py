def get_permutation(base, pos, r_arr):
    for i in range(6):
        r_arr[i] = pos % base
        pos //= base


def get_permutation_py(base, pos):
    res = [0] * 6
    get_permutation(base, pos, res)
    return res


item_profs = [
    'armouring',
    'tailoring',
    'weaponsmithing',
    'woodworking',
    'jeweling',
]
consu_profs = [
    'cooking',
    'alchemism',
    'scribing',
]
