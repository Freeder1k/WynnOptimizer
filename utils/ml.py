import numpy as np
import build.item
import build.build
import pandas as pd
import utils.skillpoints as sp
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error

elements = ['neutral', 'earth', 'thunder', 'water', 'fire', 'air']
Elements = ['Neutral', 'Earth', 'Thunder', 'Water', 'Fire', 'Air']
damageTypes = ["damage", "earthDamage", "thunderDamage",  "waterDamage", "fireDamage", "airDamage"]
types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'ring', 'bracelet', 'necklace']
masterybonus = [0, 20, 10, 15, 15 ,15]


def build_loop(weapon, items, typs, build_items, i):
    t_items = [itm for itm in items if itm.type == typs[0]]
    found = False
    b = None
    while not found and len(t_items) > 0:
        build_items[i] = np.random.choice(t_items)
        b = build.build.Build(weapon, *build_items)
        reqsp, bonsp = b.calc_sp()
        if sum(reqsp) >= 205:
            t_items.remove(build_items[i])
            build_items[i] = build.item.NO_ITEM
        else:
            if len(typs)>1:
                b, found = build_loop(weapon, items, typs[1:], build_items, i+1)
            else:
                return b, True
    return b, found

def generate_valid_build(weapon, items):
    typs = np.random.permutation(types)
    build_items = 8*[build.item.NO_ITEM]
    b, f = build_loop(weapon, items, typs, build_items, 0)
    return b

def generate_valid_dataset(weapon, items, score_fn, mastery, relevant_ids, n=5000):
    rows, scores = [], []
    for i in range(n):
        b = generate_valid_build(weapon, items)
        builditem = sp.add_sp(b.build(), *b.calc_sp())
        for typ,mas,bon in zip(damageTypes, mastery, masterybonus):
            builditem.identifications[typ] += bon*mas
        buildscore = score_fn(builditem)

        x = {iden: builditem.identifications[iden].max for iden in relevant_ids}
        rows.append(x)
        scores.append(buildscore)
    print("generated dataset")
    return pd.DataFrame(rows, columns=relevant_ids), np.array(scores)

def relevant_ids(base_dmg, melee=False):
    if melee:
        smstr = 'mainAttack'
        smStr = 'MainAttack'
    else:
        smstr = 'spell'
        smStr = 'Spell'
    relevant_ids = [f'raw{smStr}Damage', f'{smstr}Damage', "elementalDamage", "rawElementalDamage", f"rawElemental{smStr}Damage", f"elemental{smStr}Damage"]
    for i in range(6):
        if base_dmg[i] > 0:
            relevant_ids += [damageTypes[i], elements[i]+f'{smStr}Damage', 'raw'+Elements[i]+'Damage', 'raw'+Elements[i]+f'{smStr}Damage']
    return relevant_ids

def train_model(X, y, hidden_layer_sizes=(2)):
    net = Pipeline([
        ("scaler", MinMaxScaler()),
        ("mlp", MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            activation="identity",
            solver="adam",
            learning_rate_init=0.001,
            max_iter=2000,
            # random_state=42,
            verbose = False
        ))
    ])

    net.fit(X, y)

    print("R^2:", r2_score(y, net.predict(X)))
    print("MSE:", mean_squared_error(y, net.predict(X)))

    return net

def quantize_model(net):
    mlp = net.named_steps["mlp"]   # or just your MLPRegressor if no pipeline
    scaler = net.named_steps["scaler"]

    weights = mlp.coefs_
    biases = mlp.intercepts_
    means = scaler.min_
    scales = scaler.scale_

    factor = 10**3

    mlp.coefs_ = [np.round(W * factor).astype(int) for W in weights]
    mlp.intercepts_ = [np.round(b * factor).astype(int) for b in biases]
    scaler.min_ = np.round(means * factor).astype(int)
    scaler.scale_ = np.round(scales * factor).astype(int)

    return net