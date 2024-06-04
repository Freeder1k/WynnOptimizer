from build.item import Crafted

skillPoints = ["", "rawStrength", "rawDexterity", "rawIntelligence", "rawDefense", "rawAgility"]


def skillpoints(build):

    req_sp = [0,0,0,0,0]
    bon_sp = [0,0,0,0,0]

    for item in [build.weapon, build.items]:
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

    return bon_sp
