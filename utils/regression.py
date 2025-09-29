import numpy as np
import build.item
import build.build
import pandas as pd
import utils.skillpoints as sp
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error
import ast

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
        reqsp, bonsp = b.calc_sp()
        builditem = sp.add_sp(b.build(), *b.calc_sp()) # For some reason this works better?
        # builditem = b.build()
        for typ,mas,bon in zip(damageTypes, mastery, masterybonus):
            builditem.identifications[typ] += bon*mas
        buildscore = score_fn(builditem)
        itemscores = sum(int(score_fn(itm)) for itm in b.items)

        x = {iden: builditem.identifications[iden].max for iden in relevant_ids}
        x['freesp'] = 204 - sum(reqsp)
        x['itmscore'] = itemscores
        rows.append(x)
        scores.append(buildscore)
    print("generated dataset")
    return pd.DataFrame(rows, columns=relevant_ids), np.array(scores)

def get_dataset(weapon, file, score_fn, mastery, relevant_ids, n=None, random=False):
    with open(file, 'r') as f:
        lines = f.readlines()
    rows, scores = [], []
    if n is None:
        n = len(lines)
    if n > len(lines):
        print(f"Number of builds available ({len(lines)}) less than amount selected ({n})!")
        n = len(lines)
    if random:
        N = np.random.choice(len(lines), n)
    else:
        N = range(n)
    for i in N:
        text = lines[i]
        data = ast.literal_eval(text)

        items = [build.item.get_item(n) for n in data[0]]
        b = build.build.Build(weapon, *items)
        reqsp, bonsp = b.calc_sp()

        builditem = sp.add_sp(b.build(), *b.calc_sp())
        # builditem = b.build()
        for typ,mas,bon in zip(damageTypes, mastery, masterybonus):
            builditem.identifications[typ] += bon*mas
        # buildscore = score_fn(builditem)
        itemscores = sum(int(score_fn(itm)) for itm in b.items)

        x = {iden: builditem.identifications[iden].max for iden in relevant_ids}
        x['freesp'] = 204 - sum(reqsp)
        x['itmscore'] = itemscores
        rows.append(x)
        scores.append(data[1])
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

class LinReg(LinearRegression):
    @property
    def coefs_(self):
        return [np.array([self.coef_]).T]
    @coefs_.setter
    def coefs_(self, value):
        # Expect a list like MLPRegressor produces
        if not isinstance(value, list) or len(value) != 1:
            print(len(value), isinstance(value, list))
            raise ValueError("coefs_ must be a list of length 1, like MLPRegressor.")
        # if not isinstance(value[0], list) or len(value[0].T) != 1:
        #     raise ValueError("coefs_ must be a list of length 1, like MLPRegressor.")
        self.coef_ = value[0].T[0]
    @property
    def intercepts_(self):
        return [np.array([self.intercept_]).T]
    @intercepts_.setter
    def intercepts_(self, value):
        # Expect a list like MLPRegressor produces
        if not isinstance(value, list) or len(value) != 1:
            raise ValueError("intercepts_ must be a list of length 1, like MLPRegressor.")
        if not isinstance(value, list) or len(value[0].T) != 1:
            raise ValueError("intercepts_ must be a list of length 1, like MLPRegressor.")
        self.intercept_ = value[0].T[0]

def train_model(X, y, hidden_layer_sizes=()):
    mlp = MLPRegressor(
        hidden_layer_sizes=hidden_layer_sizes,
        activation="identity",
        solver="adam",
        learning_rate_init=0.001,
        max_iter=2000,
        # random_state=42,
        verbose = False
    )
    if hidden_layer_sizes == ():
        net = Pipeline([
            ("scaler", MinMaxScaler()),
            ("model", LinReg())
        ])
    else:
        net = Pipeline([
            ("scaler", MinMaxScaler()),
            ("model", mlp)
        ])

    net.fit(X, y)


    print("R^2:", r2_score(y, net.predict(X)))
    print("MSE:", mean_squared_error(y, net.predict(X)))

    return net

def quantize_model(net):
    mlp = net.named_steps["model"]
    scaler = net.named_steps["scaler"]

    weights = mlp.coefs_
    biases = mlp.intercepts_
    means = scaler.min_
    scales = scaler.scale_

    factor = 10**3

    mlp.coefs_ = [np.round(W * factor).astype(int) for W in weights]
    mlp.intercepts_ = [np.round(b * factor**(i+2)*10).astype(int) for i,b in enumerate(biases)]
    scaler.min_ = np.round(means * factor * 10).astype(int)
    scaler.scale_ = np.round(scales * factor * 10).astype(int)

    return net