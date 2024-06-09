speed_conv = {"super_slow": 0.51, "very_slow": 0.83, "slow": 1.5, "normal": 2.05, "fast": 2.5, "very_fast": 3.1, "super_fast": 4.3}  # weapon speed modifier
mastery_max = [0,4,8,4,5,4]
mastery_min = [0,2,1,2,3,3]
dTypes = ["n","e","t","w","f","a"]
damageTypes = ["damage", "earthDamage", "thunderDamage",  "waterDamage", "fireDamage", "airDamage"]
elements = ['neutral', 'earth', 'thunder', 'water', 'fire', 'air']
Elements = ['Neutral', 'Earth', 'Thunder', 'Water', 'Fire', 'Air']
skillPoints = ["", "rawStrength", "rawDexterity", "rawIntelligence", "rawDefense", "rawAgility"]
powderConv = {"e":(0.46,13,11),"t":(0.28,20,5),"w":(0.32,11,9),"a":(0.35,14,8),"f":(0.37,12,10)}


def base_dmg(weapon, powders, spellmod, masteries):
    speedmod = speed_conv[weapon.attackSpeed]
    weapon_dmg_max = [weapon.damage[dtype].max for dtype in damageTypes]
    weapon_dmg_min = [weapon.damage[dtype].min for dtype in damageTypes]  # do this not for max?

    neutral_max = weapon_dmg_max[0]
    neutral_min = weapon_dmg_min[0]
    for powder in powders:
        weapon_dmg_max[dTypes.index(powder)] += neutral_max*powderConv[powder][0] + powderConv[powder][1]
        weapon_dmg_max[0] -= neutral_max*powderConv[powder][0]
        weapon_dmg_min[dTypes.index(powder)] += neutral_min*powderConv[powder][0] + powderConv[powder][2]
        weapon_dmg_min[0] -= neutral_min*powderConv[powder][0]

    # calculate base dmg without IDs
    base_dmg_max = [0,0,0,0,0,0]
    for i, dmg in enumerate(weapon_dmg_max):
        base_dmg_max[i] = dmg * spellmod[0]  # neutral modifier applies to individual element
        base_dmg_max[i] += sum(weapon_dmg_max) * spellmod[i]  # elemental modifier applies to total damage
        base_dmg_max[i] *= speedmod
        if base_dmg_max[i] != 0:
            base_dmg_max[i] += int(masteries[i]) * mastery_max[i]
    # neutral base only uses neutral dmg
    base_dmg_max[0] = weapon_dmg_max[0] * speedmod * spellmod[0]
    base_dmg_min = [0,0,0,0,0,0]
    for i, dmg in enumerate(weapon_dmg_min):
        base_dmg_min[i] = dmg * spellmod[0]  # neutral modifier applies to individual element
        base_dmg_min[i] += sum(weapon_dmg_min) * spellmod[i]  # elemental modifier applies to total damage
        base_dmg_min[i] *= speedmod
        if base_dmg_min[i] != 0:
            base_dmg_min[i] += int(masteries[i]) * mastery_min[i]
    # neutral base only uses neutral dmg
    base_dmg_min[0] = weapon_dmg_min[0] * speedmod * spellmod[0]

    return base_dmg_max, base_dmg_min

def avg_dmg(min, max, ids, spellmodsum, crit=True):
    return sum(true_dmg(min, ids, spellmodsum, crit) + true_dmg(max, ids, spellmodsum, crit))/2

def true_dmg(base, ids, spellmodsum, crit=True):
    pct = [ids["spellDamage"].max] + 5 * [ids["spellDamage"].max + ids['elementalSpellDamage'].max]
    for i in range(6):
        pct[i] += ids[damageTypes[i]].max + ids[elements[i]+'SpellDamage'].max
        pct[i] += 100*spToPct(ids[skillPoints[i]].max)
        pct[i] = pct[i]*0.01

    strePct = spToPct(ids["rawStrength"].max)
    dexPct = spToPct(ids["rawDexterity"].max)
    raw = [ids["rawSpellDamage"].max] + 5 * [ids["rawSpellDamage"].max + ids['rawElementalDamage'].max + ids['rawElementalSpellDamage'].max]

    # add IDs for final damage
    damage = [0,0,0,0,0,0]
    for i, dmg in enumerate(base):
        damage[i] = dmg * (1 + pct[i])
        damage[i] += spellmodsum * (dmg/sum(base) * raw[i] + ids["raw"+Elements[i]+"SpellDamage"].max + ids["raw"+Elements[i]+"Damage"].max)
        damage[i] *= 1 + strePct + int(crit) * dexPct  # (since dex is crit chance, it's just an average)

    return damage


def spToPct(sp):  # skillpoints to percentage
    if sp <= 0:
        return 0.0
    elif sp >= 150:
        sp = 150
    return sppct[sp]

# This is more efficient than using the function
sppct = [0.0, 0.009907999999999998, 0.01972484640000003, 0.029451377813119947, 0.039088425137239285, 0.04863681162597668, 0.05809735295901775, 0.06747085731179477, 0.07675812542452624, 0.08595995067062062, 0.09507711912445085, 0.10411040962850589, 0.11306059385992366, 0.12192843639641239, 0.13071469478156544, 0.13942011958957506, 0.14804545448935097, 0.15659143630804884, 0.1650587950940148, 0.17344825417914989, 0.18176053024070174, 0.18999633336248728, 0.19815636709555243, 0.2062413285182733, 0.21425190829590515, 0.22218879073958286, 0.23005265386477866, 0.23784416944922282, 0.24556400309028986, 0.2532128142618592, 0.2607912563706502, 0.2682999768120402, 0.2757396170253694, 0.28311081254873594, 0.29041419307328764, 0.2976503824970134, 0.30481999897804085, 0.3119236549874429, 0.31896195736155847, 0.3259355073538321, 0.3328449006861768, 0.339690727599864, 0.34647357290594527, 0.3531940160352105, 0.3598526310876866, 0.3664499868816799, 0.3729866470023685, 0.37946316984994666, 0.38588010868732714, 0.39223801168740374, 0.3985374219798796, 0.40477887769766474, 0.41096291202284624, 0.4170900532322361, 0.42316082474249944, 0.42917574515486856, 0.43513532829944374, 0.44104008327908883, 0.4468905145129213, 0.4526871217794024, 0.45843040025903187, 0.4641208405766488, 0.46975892884334364, 0.475345146697985, 0.4808799713483634, 0.48636387561195854, 0.49179732795632847, 0.4971807925391303, 0.5025147292477703, 0.5077995937386909, 0.5130358374762949, 0.518223907771513, 0.5233642478200151, 0.5284572967400709, 0.5335034896100622, 0.5385032575056496, 0.5434570275365977, 0.5483652228832611, 0.553228262832735, 0.5580465628146739, 0.5628205344367789, 0.5675505855199606, 0.5722371201331768, 0.5768805386279517, 0.5814812376725745, 0.5860396102859868, 0.5905560458713557, 0.5950309302493393, 0.5994646456910454, 0.6038575709506877, 0.6082100812979414, 0.6125225485500004, 0.6167953411033404, 0.6210288239651898, 0.6252233587847099, 0.6293793038838906, 0.6334970142881589, 0.6375768417567079, 0.641619134812546, 0.6456242387722706, 0.6495924957755658, 0.6535242448144306, 0.657419821762138, 0.6612795594019262, 0.6651037874554285, 0.6688928326108387, 0.6726470185508188, 0.6763666659801514, 0.6800520926531339, 0.683703613400725, 0.6873215401574384, 0.69090618198799, 0.6944578451137005, 0.6979768329386544, 0.7014634460756188, 0.7049179823717232, 0.7083407369339032, 0.7117320021541115, 0.7150920677342937, 0.7184212207111382, 0.7217197454805958, 0.7249879238221744, 0.7282260349230101, 0.7314343554017186, 0.7346131593320228, 0.737762718266168, 0.7408833012581194, 0.7439751748865446, 0.7470386032775884, 0.7500738481274347, 0.7530811687246622, 0.7560608219723954, 0.7590130624102494, 0.761938142236075, 0.7648363113275032, 0.7677078172632903, 0.770552905344468, 0.7733718186152988, 0.776164797884038, 0.7789320817435049, 0.7816739065914647, 0.7843905066508233, 0.7870821139896357, 0.7897489585409311, 0.7923912681223544, 0.795009268455629, 0.7976031831858371, 0.8001732339005274, 0.8027196401486427, 0.8052426194592751, 0.8077423873602497]
