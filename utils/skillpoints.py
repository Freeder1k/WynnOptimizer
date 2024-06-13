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


def uncrafted_sp(items):
    bon_sp=[0,0,0,0,0]
    req_sp = [0,0,0,0,0]
    for i in range(5):
        reqs = []
        bons = []
        for item in items:
            req = item.requirements[sp[i]]
            if req == 0:
                reqs.append(-1000)
            else:
                reqs.append(req)
            bons.append(item.identifications[skillPoints[i]].max)
        sums = [r + b for r, b in zip(reqs, bons)]
        max_index = sums.index(max(sums))
        max_req = reqs[max_index]
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
