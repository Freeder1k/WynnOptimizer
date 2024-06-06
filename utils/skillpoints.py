from build.item import Crafted
import math
from collections import namedtuple

skillPoints = ["rawStrength", "rawDexterity", "rawIntelligence", "rawDefence", "rawAgility"]
sp = ["str","dex","int","def","agi"]

SkillpointsTuple = namedtuple('SkillpointsTuple', ['str', 'dex', 'int', 'defe', 'agi'])

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
    nbon_sp=[0,0,0,0,0]
    # do items that dont have any requirements
    remain = []
    for item in items:
        if any(req > 0 for req in item.requirements.get_requirements()):
            remain.append(item)
        else:
            for i in range(5):
                s = item.identifications[skillPoints[i]].max
                if s > 0:
                    bon_sp[i] += s
                else:
                    nbon_sp[i] += s

    # do items that have requirements
    req_sp = [0,0,0,0,0]
    for i in range(5):
        splist = []
        for item in remain:
            req = item.requirements[sp[i]]
            bon = item.identifications[skillPoints[i]].max
            name = item.name
            splist.append((req, bon, name))
        sorted_list = sorted(splist, key=lambda x: x[0])  # sort by lowest requirement

        for j, (req, bon, name) in enumerate(sorted_list):  # on last item do negative skillpoints
            if j == len(sorted_list) - 1:
                bon_sp[i] += nbon_sp[i]
            if req > 0:
                req_sp[i] = max(req_sp[i], req - bon_sp[i])
                bon_sp[i] += bon
            else:
                if bon > 0:
                    bon_sp[i] += bon
                else:
                    nbon_sp[i] += bon

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
