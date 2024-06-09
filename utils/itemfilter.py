import build.item

types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'bracelet', 'necklace']
elements = ['neutral', 'earth', 'thunder', 'water', 'fire', 'air']
Elements = ['Neutral', 'Earth', 'Thunder', 'Water', 'Fire', 'Air']
damageTypes = ["damage", "earthDamage", "thunderDamage",  "waterDamage", "fireDamage", "airDamage"]
set_rings = ['Intensity', 'Breezehands', 'Coral Ring', 'Moon Pool Circlet']

def remove_bad_items(base_dmg, items: list[build.item.Item]) -> list[build.item.Item]:
    relevant_ids = ["rawStrength", "rawDexterity", "rawIntelligence", "rawDefense", "rawAgility", 'rawSpellDamage',
                    'spellDamage', "elementalDamage", "rawElementalDamage", "rawElementalSpellDamage", "elementalSpellDamage"]
    for i in range(6):
        if base_dmg[i] > 0:
            relevant_ids += [damageTypes[i], elements[i]+'SpellDamage', 'raw'+Elements[i]+'Damage', 'raw'+Elements[i]+'SpellDamage']

    good_items = []
    for t in types:
        t_items = [i for i in items if i.type == t]
        for itm in t_items:
            good = True
            for itm2 in t_items:
                if all(itm.requirements >= itm2.requirements) and itm2.name not in set_rings:
                    if all(itm2.identifications[id].max >= itm.identifications[id].max for id in relevant_ids):
                        if any(itm2.identifications[id].max > itm.identifications[id].max for id in relevant_ids):
                            good = False
                            break
            if good:
                good_items.append(itm)

    return good_items


def set_item_of_type(items: list[build.item.Item], itm: build.item.Item, typ: str) -> list[build.item.Item]:
    items = [i for i in items if i.type != typ]
    items.append(itm)
    return items


def set_items_of_type(items: list[build.item.Item], itms:  list[build.item.Item], typ: str) -> list[build.item.Item]:
    items = [i for i in items if i.type != typ]
    items += itms
    return items
