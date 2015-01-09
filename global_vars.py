epsilon = 0.000001

class ParsedInput:
    def __init__(self, A, b, cnf, row_dict, col_dict):
        self.A = A
        self.b = b
        self.cnf = cnf
        self.row_dict = row_dict
        self.col_dict = col_dict
