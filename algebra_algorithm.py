import re, copy
from collections import defaultdict
import global_vars as gv

EQUATION_OPERATORS = ['<', '<=', '=', '>=', '>']

class Equation(object):
    '''
    This is immutable because we don't want the contents to change after it is hashed.
    '''
    __slots__ = ['left_hand_side', 'operator', 'right_hand_side']
    def __setattr__(self, *args):
        raise TypeError("can't modify immutable instance")

    __delattr__ = __setattr__

    def __init__(self, left_hand_side, operator, right_hand_side):
        super(Equation, self).__setattr__('left_hand_side', left_hand_side)
        super(Equation, self).__setattr__('operator', operator)
        super(Equation, self).__setattr__('right_hand_side', right_hand_side)

    def __str__(self):
        return str(self.left_hand_side) + str(self.operator) + str(self.right_hand_side)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return int(self.__str__().encode('hex'), 16)

def parse_term(term):
    match = re.search(r'([-]?[0-9][\.]?[0-9]{0,})?(\*?([a-z]+[0-9]*))?$', term)
    coefficient = 1
    if match.group(1):
        if match.group(1) == '-':
            coefficient = -1
        else:
            coefficient = float(match.group(1))
    # very cleverly, the variable will be None if there isn't one
    variable = match.group(3)
    return (coefficient, variable)

def simplexify_equation(equation):
    '''
    convert to Ax <= b form and return an equation object with these values
    '''
    b_side_multiplier = -1
    lhs, op, rhs = None, equation.operator, None
    b_side_epsilon = 0
    b_side = 0
    if op == '<':
        op = '<='
        b_side_epsilon -= gv.epsilon
    if op == '>':
        op = '>='
        b_side_epsilon -= gv.epsilon

    if op == '<=':
        simplex_ax_side = move_terms_from_to(equation.right_hand_side, equation.left_hand_side)
    else:
        simplex_ax_side = move_terms_from_to(equation.left_hand_side, equation.right_hand_side)
        op = reverse_operator(op)

    try:
        b_side = b_side_multiplier * simplex_ax_side[None]
        del simplex_ax_side[None]
    except(KeyError):
        pass

    b_side += b_side_epsilon
    simplex_ax_side = convert_to_unrestricted_form(simplex_ax_side)

    return Equation(simplex_ax_side, op, b_side)

def convert_to_unrestricted_form(dict_expression):
    '''
    assumes there are no constants!
    '''
    dict_urs_form = {}
    for key in dict_expression:
        a, b = dict_expression[key], -dict_expression[key]
        dict_urs_form[key+'p'] = a
        dict_urs_form[key+'pp'] = b
    return dict_urs_form

def reverse_operator(operator):
    if operator == '=':
        return '='
    elif operator == '>=':
        return '<='
    elif operator == '>':
        return '<'
    elif operator == '<=':
        return '>='
    elif operator == '<':
        return '>'
    elif operator == '!=':
        return '!='
    else:
        print 'bad math operator'
        assert(False)

def move_terms_from_to(side_from, side_to):
    defaultdict_from = convert_to_dict(side_from)
    defaultdict_to = convert_to_dict(side_to)
    for key, value in defaultdict_from.iteritems():
        defaultdict_to[key] -= defaultdict_from[key]
    dict_no_zeros = remove_zero_terms(defaultdict_to)
    return dict_no_zeros

def remove_zero_terms(expression):
    simplified_expression = {}
    for variable, coefficient in expression.iteritems():
        if expression[variable] != 0:
            simplified_expression[variable] = coefficient
    return simplified_expression

def split_equation(equation):
    tokens = equation.split()
    left_hand_side = []
    right_hand_side = []
    left_side = True
    operator = None
    for token in tokens:
        if token in EQUATION_OPERATORS:
            left_side = False
            operator = token
            continue
        if left_side:
            left_hand_side.append(token)
        else:
            right_hand_side.append(token)
    return Equation(left_hand_side, operator, right_hand_side)

def negate_simplex(equation):
    '''
    only works on simplex form
    '''
    lhs = copy.deepcopy(equation.left_hand_side)
    rhs = copy.deepcopy(equation.right_hand_side)
    for key in lhs:
        lhs[key] *= -1
    rhs *= -1
    rhs -= gv.epsilon
    return Equation(lhs, '<=', rhs)

def convert_to_dict(expression):
    vars_coefficients = defaultdict(int)
    negate = False
    for term in expression:
        if term == '-':
            negate = True
        elif term == '+':
            negate = False
        else:
            coefficient, variable = parse_term(term)
            if negate:
                coefficient *= -1
            vars_coefficients[variable] += coefficient
    return vars_coefficients

def convert_to_simplex_form(equation):
    obj_equation = split_equation(equation)
    obj_simplex_equation = simplexify_equation(obj_equation)
    return obj_simplex_equation
