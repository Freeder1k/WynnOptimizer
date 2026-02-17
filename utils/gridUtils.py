# Crafting grid utilities

def unflatten(i):
    return i % 2, i // 2

def flatten(x, y):
    return y * 2 + x

def is_left(i, j):
    x_i, y_i = unflatten(i)
    x_j, y_j = unflatten(j)
    return x_i < x_j and y_i == y_j

def is_right(i, j):
    x_i, y_i = unflatten(i)
    x_j, y_j = unflatten(j)
    return x_i > x_j and y_i == y_j

def is_above(i, j):
    x_i, y_i = unflatten(i)
    x_j, y_j = unflatten(j)
    return y_i < y_j and x_i == x_j

def is_under(i, j):
    x_i, y_i = unflatten(i)
    x_j, y_j = unflatten(j)
    return y_i > y_j and x_i == x_j

def is_touching(i, j):
    x_i, y_i = unflatten(i)
    x_j, y_j = unflatten(j)
    return abs(x_i - x_j) == 1 and abs(y_i - y_j) == 0 or abs(x_i - x_j) == 0 and abs(y_i - y_j) == 1

def is_not_touching(i, j):
    return i != j and not is_touching(i, j)