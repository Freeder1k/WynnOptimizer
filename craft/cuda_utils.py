import numba
from llvmlite import ir
from numba import cuda
from numba.cuda.extending import intrinsic

from craft.utils import get_permutation

CHARGES = 0
DURATION = 1
DURABILITY = 2
REQ_STR = 3
REQ_DEX = 4
REQ_INT = 5
REQ_DEF = 6
REQ_AGI = 7
MOD_LEFT = 8
MOD_RIGHT = 9
MOD_ABOVE = 10
MOD_UNDER = 11
MOD_TOUCH = 12
MOD_NOT_TOUCH = 13
IDS = 14


def calc_recipe_cuda_function_factory(id_count: int):
    def calc_recipe(ingredients, recipe_args, mods, res_recipe):
        for i in range(6):
            ingr = ingredients[recipe_args[i]]
            # TODO compare speed between float multiplication and // 100

            res_recipe[CHARGES] += ingr[CHARGES]
            res_recipe[DURATION] += ingr[DURATION]
            res_recipe[DURABILITY] += ingr[DURABILITY] // 1000
            res_recipe[REQ_STR] += ingr[REQ_STR] * mods[i] // 100
            res_recipe[REQ_DEX] += ingr[REQ_DEX] * mods[i] // 100
            res_recipe[REQ_INT] += ingr[REQ_INT] * mods[i] // 100
            res_recipe[REQ_DEF] += ingr[REQ_DEF] * mods[i] // 100
            res_recipe[REQ_AGI] += ingr[REQ_AGI] * mods[i] // 100
            for k in range(id_count):
                j = (k * 2) + IDS
                if mods[i] > 0:
                    res_recipe[j] += ingr[j] * mods[i] // 100
                    res_recipe[j + 1] += ingr[j + 1] * mods[i] // 100
                elif mods[i] < 0:
                    res_recipe[j] += ingr[j + 1] * mods[i] // 100
                    res_recipe[j + 1] += ingr[j] * mods[i] // 100

    return cuda.jit(calc_recipe, device=True, fastmath=True)


@cuda.jit(device=True, fastmath=True)
def calc_mods(ingredients, r, mod_arr):
    mod_arr[0] = (100
                  + ingredients[r[1]][MOD_LEFT] + ingredients[r[1]][MOD_TOUCH]
                  + ingredients[r[2]][MOD_ABOVE] + ingredients[r[2]][MOD_TOUCH]
                  + ingredients[r[3]][MOD_NOT_TOUCH]
                  + ingredients[r[4]][MOD_ABOVE] + ingredients[r[4]][MOD_NOT_TOUCH]
                  + ingredients[r[5]][MOD_NOT_TOUCH])
    mod_arr[1] = (100
                  + ingredients[r[0]][MOD_RIGHT] + ingredients[r[0]][MOD_TOUCH]
                  + ingredients[r[2]][MOD_NOT_TOUCH]
                  + ingredients[r[3]][MOD_ABOVE] + ingredients[r[3]][MOD_TOUCH]
                  + ingredients[r[4]][MOD_NOT_TOUCH]
                  + ingredients[r[5]][MOD_ABOVE] + ingredients[r[5]][MOD_NOT_TOUCH])
    mod_arr[2] = (100
                  + ingredients[r[0]][MOD_UNDER] + ingredients[r[0]][MOD_TOUCH]
                  + ingredients[r[1]][MOD_NOT_TOUCH]
                  + ingredients[r[3]][MOD_LEFT] + ingredients[r[3]][MOD_TOUCH]
                  + ingredients[r[4]][MOD_ABOVE] + ingredients[r[4]][MOD_TOUCH]
                  + ingredients[r[5]][MOD_NOT_TOUCH])
    mod_arr[3] = (100
                  + ingredients[r[0]][MOD_NOT_TOUCH]
                  + ingredients[r[1]][MOD_UNDER] + ingredients[r[1]][MOD_TOUCH]
                  + ingredients[r[2]][MOD_RIGHT] + ingredients[r[2]][MOD_TOUCH]
                  + ingredients[r[4]][MOD_NOT_TOUCH]
                  + ingredients[r[5]][MOD_ABOVE] + ingredients[r[5]][MOD_TOUCH])
    mod_arr[4] = (100
                  + ingredients[r[0]][MOD_UNDER] + ingredients[r[0]][MOD_NOT_TOUCH]
                  + ingredients[r[1]][MOD_NOT_TOUCH]
                  + ingredients[r[2]][MOD_UNDER] + ingredients[r[2]][MOD_TOUCH]
                  + ingredients[r[3]][MOD_NOT_TOUCH]
                  + ingredients[r[5]][MOD_LEFT] + ingredients[r[5]][MOD_TOUCH])
    mod_arr[5] = (100
                  + ingredients[r[0]][MOD_NOT_TOUCH]
                  + ingredients[r[1]][MOD_UNDER] + ingredients[r[1]][MOD_NOT_TOUCH]
                  + ingredients[r[2]][MOD_NOT_TOUCH]
                  + ingredients[r[3]][MOD_UNDER] + ingredients[r[3]][MOD_TOUCH]
                  + ingredients[r[4]][MOD_RIGHT] + ingredients[r[4]][MOD_TOUCH])


get_permutation_cuda = cuda.jit(get_permutation, device=True)


@intrinsic
def cuda_clock64(typingctx):
    sig = numba.types.uint64()

    def codegen(context, builder, sig, args):
        function_type = ir.FunctionType(ir.IntType(64), [])
        instruction = "mov.u64 $0, %clock64;"
        clock64 = ir.InlineAsm(function_type, instruction, "=l",
                               side_effect=True)
        return builder.call(clock64, [])

    return sig, codegen
