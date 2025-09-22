from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter


spellmods = [[1.8,0,0,0,0.2,0], [1.4,0,0,0,0,0]]
weapon = build.item.get_weapon("Divzer").set_powders(["t", "t", "t"])
skilltree = '1Tl-x37BNd0'
mastery = [False, True, False, False, True]  # Elemental masteries from skilltree [ETWFA]
base_dmg_maxs, base_dmg_mins = [], []
base_dmg_max, base_dmg_min = [0,0,0,0,0,0], [0,0,0,0,0,0]
for spellmod in spellmods:
    ma, mi = dmgcalc.base_dmg(weapon, spellmod, mastery)
    base_dmg_maxs.append(ma)
    base_dmg_mins.append(mi)
    for i in range(6):
        base_dmg_max[i] += ma[i]
        base_dmg_min[i] += mi[i]

consus = build.item.Item("consus",
                         "consumable",
                         build.item.IdentificationList.from_api_data(
                             {"rawStrength": 50, "rawDexterity": 55, "rawIntelligence": 45, "manaRegen": 12, "manaSteal": 56, "rawSpellDamage": 575, "spellDamage": 206, "elementalDamage": 33, "thunderDamage": 150}),
                         build.item.Requirements(0, 0, 0, 0, 0, 0))

def score(itm: build.item.Item) -> float:
    dmg = 0
    for spellmod, base_dmg_max, base_dmg_min in zip(spellmods, base_dmg_maxs, base_dmg_mins):
        dmg += dmgcalc.avg_dmg(base_dmg_min, base_dmg_max, itm.identifications, sum(spellmod))
    return dmg

# Divzer is basically just thunder damage so gonna simplyfy a bit
spellmodsum = sum(sum(spellmod) for spellmod in spellmods)
def score_model(model, items, item_vars, sp_vars):
    f = 1
    base = (base_dmg_max[2] + base_dmg_min[2])/2

    # Skillpoints
    skillpoints = [0,0,0,0,0,0]
    free_sp = 204 - sum(sp_vars)
    item_sp = []
    for i in range(5):
        a = [weapon.identifications[dmgcalc.skillPoints[i+1]].max, sp_vars[i]]
        for itm, x in zip(items, item_vars):
            if itm.identifications[dmgcalc.skillPoints[i+1]].max != 0:
                a.append(itm.identifications[dmgcalc.skillPoints[i+1]].max * x)
        item_sp.append(sum(a))

    item_sp[0] = item_sp[0] + free_sp
    for i in range(5):
        if i == 3:# or i<=1:
            skillpoints[i+1] = dmgcalc.spToPct_model2(model, item_sp[i], dmgcalc.sptypes[i])  # directly add base to sp
    strdexvar = model.new_int_var(f*100, f*300, f"strdexvar")
    model.add(strdexvar == f*100 + skillpoints[1] + skillpoints[2])

    # damage bonus
    item_dmg = [int(f*10*mastery[2]*base)]
    for itm, x in zip(items + [weapon], item_vars + [1]):
        item_pct = itm.identifications["spellDamage"].max + itm.identifications['elementalSpellDamage'].max
        item_raw_n = itm.identifications["rawSpellDamage"].max
        item_raw_e = itm.identifications['rawElementalDamage'].max + itm.identifications['rawElementalSpellDamage'].max

        item_pct += itm.identifications["thunderDamage"].max + itm.identifications['thunder'+'SpellDamage'].max
        item_raw_elemental = itm.identifications["raw"+'Thunder'+"SpellDamage"].max + itm.identifications["raw"+'Thunder'+"Damage"].max
        item_raw = (item_raw_n + item_raw_e) + item_raw_elemental

        raw, pct = 0,0
        if item_raw != 0:
            raw = f*100 * spellmodsum * item_raw
        if item_pct != 0:
            pct = f*base * item_pct
        item_dmg.append(int(pct + raw) * x)

    dmg = int(base*f*100) + sum(item_dmg) + int(base)*skillpoints[4]

    dmgvar = model.new_int_var(0, 2147483647, f"dmgvar")
    model.add(dmgvar == dmg)
    damage = model.new_int_var(0, 2147483647, f"damage")
    model.add_multiplication_equality(damage, [dmgvar,strdexvar])
    return damage + 650000*f*(item_sp[0] + item_sp[1] ), *item_sp


items = list(itm for itm in build.item.get_all_items().values() if score(itm) > score(build.item.NO_ITEM) and itm.requirements.level <= 100)
items = itemfilter.remove_bad_items(base_dmg_max, items)
# items = itemfilter.set_item(items, build.item.get_item("Time Rift"))
# itemnames = ("Caesura", "Soul Signal", "Chaos-Woven Greaves", "Broken Balance", "Yang", "Yang", "Diamond Hydro Bracelet", "Amanuensis")
# items = []
# for i in itemnames:
#     items.append(build.item.get_item(i))


class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        self.set_model_function(score_model)
        self.set_useModelFunction(True)
        # self.set_requirement_max('def', 0)
        # self.set_requirement_max('agi', 0)
        self.add_lower_bound(lambda itm: itm.identifications['baseHealth'].max + itm.identifications['rawHealth'].max, 5000)
        self.set_identification_min("manaRegen", 70)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)
        self.set_skilltree(skilltree)
        self.set_sdfactor(2)
        self.set_consus(consus)
        # self.set_sp_max('str', 150)
        # self.set_sp_min('str', 40)
        # self.set_sp_max('dex', 150)
        # self.set_sp_min('dex', 40)
        # self.set_sp_min('def', 50)
