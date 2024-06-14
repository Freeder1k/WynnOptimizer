from build.item import Crafted
import math

skillPoints = ["rawStrength", "rawDexterity", "rawIntelligence", "rawDefence", "rawAgility"]
sp = ["str","dex","int","def","agi"]


def skillpoints(build):

    uncrafteds = []
    crafteds = [build.weapon]
    for item in build.items:
        if isinstance(item, Crafted):
            crafteds.append(item)
        else:
            uncrafteds.append(item)

    req_sp, bon_sp = uncrafted_sp(uncrafteds)

    req_sp, bon_sp = crafted_sp(crafteds, req_sp, bon_sp)

    return req_sp, bon_sp

# There are very few cases in which this is incorrect:
# (https://hppeng-wynn.github.io/builder/?v=7#9_07F0mG0uS06n2SK2SL2SM2SN05e0t190y-v-v1g000000z0z0+0+0+0+0-1Tjdxa+LQK30)
# returns: ([52, 50, 32, 0, 0], [3, 13, 28, -7, -7]) instead of ([52, 60, 32, 0, 0], [3, 13, 28, -7, -7])
# There are probably also complete (good) builds that this would apply to,
# but it's a very specific problem and the rigorous method is much slower.
def uncrafted_sp(items):
    bon_sp=[0,0,0,0,0]
    req_sp = [0,0,0,0,0]
    for i in range(5):
        reqs = []
        bons = []
        nbons = []
        max_sum = 0
        max_index = 0
        for j, item in enumerate(items):
            req = item.requirements[sp[i]]
            bon = item.identifications[skillPoints[i]].max
            bons.append(bon)
            if bon < 0:
                nbons.append(bon)
            if req == 0:
                reqs.append(-1000)
                continue
            reqs.append(req)
            if req + bon > max_sum:
                max_sum = req + bon
                max_index = j
            elif req + bon == max_sum:
                if bon > bons[max_index]:
                    max_index = j

        max_req = reqs[max_index]-sum(nbons)
        bonus = sum(min(bon,max(0,max_req-req)) for req, bon in zip(reqs, bons))
        req_sp[i] = max(0, max_req - bonus)
        bon_sp[i] = sum(bons)

    return req_sp, bon_sp


def crafted_sp(items, req_sp, bon_sp):
    _bon_sp = [0,0,0,0,0]
    for i in range(5):
        for item in items:
            req = item.requirements[sp[i]]
            if req > 0:
                req_sp[i] = max(req_sp[i], req - bon_sp[i])
            _bon_sp[i] += item.identifications[skillPoints[i]].max

    bon_sp = [bon_sp[i] + _bon_sp[i] for i in range(5)]

    return req_sp, bon_sp


def add_sp(item, req_sp, bon_sp):
    req_str = req_sp[0]
    req_dex = req_sp[1]
    extra = 200-sum(req_sp)
    s = req_str + bon_sp[0]
    d = req_dex + bon_sp[1]

    if extra > 0:
        if d+extra < s:
            req_dex += extra
        elif s+extra < d:
            req_str += extra
        else:
            sdr = s + d + extra
            req_str += math.ceil(sdr/2) - s
            req_dex += math.floor(sdr/2) - d

    item.identifications[skillPoints[0]] += req_str
    item.identifications[skillPoints[1]] += req_dex
    item.identifications[skillPoints[2]] += req_sp[2]
    item.identifications[skillPoints[3]] += req_sp[3]
    item.identifications[skillPoints[4]] += req_sp[4]
    return item
