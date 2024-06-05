from build.item import Crafted
import math

skillPoints = ["rawStrength", "rawDexterity", "rawIntelligence", "rawDefense", "rawAgility"]


def skillpoints(build):

    req_sp = [0,0,0,0,0]
    bon_sp = [0,0,0,0,0]

    for item in [build.weapon] + list(build.items):
        if not isinstance(item, Crafted):
            for i, req in enumerate(item.requirements.get_requirements()):
                if req > req_sp[i]+bon_sp[i]:
                    req_sp[i] = req - bon_sp[i]
                elif req < req_sp[i]:
                    req_sp[i] = max(req, req_sp[i] - item.identifications[skillPoints[i]].max)
                bon_sp[i] += item.identifications[skillPoints[i]].max
        else:
            for i, req in enumerate(item.requirements.get_requirements()):
                if req > req_sp[i]+bon_sp[i]:
                    req_sp[i] = req - bon_sp[i]

    return req_sp, bon_sp


def add_sp(item, req_sp, bon_sp):
    extra = 200-sum(req_sp)
    s = req_sp[0] + bon_sp[0]
    d = req_sp[1] + bon_sp[1]

    if d+extra < s:
        req_sp[1] += extra
    elif s+extra < d:
        req_sp[0] += extra
    else:
        sdr = s + d + extra
        req_sp[0] += math.ceil(sdr/2) - s
        req_sp[1] += math.floor(sdr/2) - d

    for i in range(5):
        item.identifications[skillPoints[i]] += req_sp[i]

    return item
