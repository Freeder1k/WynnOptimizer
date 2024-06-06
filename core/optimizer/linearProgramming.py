import scipy.optimize as opt

class IntegerLinearProgramm:
    def __init__(self, c, A_ub, b_ub, A_eq, b_eq, bounds=(0,1)):
        self.c = c
        self.A_ub = A_ub
        self.b_ub = b_ub
        self.A_eq = A_eq
        self.b_eq = b_eq
        self.bounds = bounds

    def solve(self):
        return opt.linprog(self.c, self.A_ub, self.b_ub, self.A_eq, self.b_eq, bounds=self.bounds, integrality=1)