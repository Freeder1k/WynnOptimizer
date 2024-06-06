from build.config.base import HybridOptimizerConfig
import build.item
from utils import dmgcalc


spellmod = [0.3, 0, 0.15, 0.1, 0, 0]  # multihit https://wynnbuilder.github.io/builder/#8_2SG2SH2SI2SJ2SK2SL2SM2SN0Qm00000000001g00001004fI0z0z0+0+0+0+0-ldxagIZu07
spellmodsum = sum(spellmod)
weapon = build.item.get_weapon("Nirvana")
base_dmg = dmgcalc.base_dmg(weapon, ["w", "w", "w"], [0.3, 0, 0.15, 0.1, 0, 0])
base_score = sum(dmgcalc.true_dmg(base_dmg, weapon.identifications, spellmodsum))

def score(item: build.item.Item, ) -> float:
    identifications = weapon.identifications + item.identifications
    return sum(dmgcalc.true_dmg(base_dmg, identifications, spellmodsum)) - base_score


items = list(build.item.get_all_items().values())


class DmgConfig(HybridOptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        #self.set_max_def_req(20)
        #self.set_max_agi_req(20)
        #self.set_identification_min(build.item.IdentificationType.RAW_STRENGTH, 20)
        #self.set_identification_min(build.item.IdentificationType.RAW_DEXTERITY, 20)
        #self.set_identification_min(build.item.IdentificationType.RAW_INTELLIGENCE, 20)
        self.set_num_builds(1000)
        self.set_weapon(weapon)
