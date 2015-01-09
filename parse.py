import sys, re, copy
from collections import defaultdict
import numpy as np
import algebra_algorithm as aa
import global_vars as gv
import dpll as dpll


BOOL_OPERATORS = ['and', 'or', 'nand', 'nor', 'xor', 'xnor', '->']
'''
(and x y) --> ( ~x ^ ~y ^ z ) ^ ( x v ~z ) ^ ( y v ~z )
(or x y) --> ( x v y v ~z ) ^ ( ~x v z ) ^ ( ~y v z )
(not x) --> ( ~x v ~z ) ^ ( x v z )
(nand x y) --> ( ~x v ~y v ~z ) ^ ( x v z ) ^ ( y v z )
(nor x y) --> ( x v y v z ) ^ ( ~x v ~z ) ^ ( ~y v ~z )
(xor x y) --> ( ~x v ~y v ~z ) ^ ( x v y v ~z ) ^ ( x v ~y v z ) ^ ( ~x v y v z )
(xnor x y) --> ( x v y v z ) ^ ( ~x v ~y v z ) ^ ( ~x v y v ~z ) ^ ( x v ~y v ~z )
(-> x y) --> ( x v y v z ) ^ ( ~x v y v ~z ) ^ ( x v ~y v z) ^ ( ~x v ~y v z )
'''

equation_counter = 0
equation_dictionary = {}
def get_associated_variable(str_equation):
    '''
    stores equation objects in simplex form. If we have a match
    on the lhs dictionary, the operator, and the rhs, we have the
    variable
    '''
    obj_simplex_form = aa.convert_to_simplex_form(remove_outer_parens(str_equation))
    global equation_dictionary
    global equation_counter
    if obj_simplex_form in equation_dictionary:
        return equation_dictionary[obj_simplex_form]
    else:
        new_var = 'q' + str(equation_counter)
        equation_dictionary[obj_simplex_form] = new_var
        equation_counter += 1
        return new_var

def remove_outer_parens(term):
    if term[0] == '(' and term[-1] == ')':
        return term[1:-1]
    else:
        return term

def fail(*error):
    if error:
        print error[0]
    exit(1)

def tseitin_transform_and(var1, var2, var3):
    return '( ~{0} v ~{1} v {2} ) ^ ( {0} v ~{2} ) ^ ( {1} v ~{2} )'\
            .format(var1, var2, var3)

def tseitin_transform_or(var1, var2, var3):
    return '( {0} v {1} v ~{2} ) ^ ( ~{0} v {2} ) ^ ( ~{1} v {2} )'\
            .format(var1, var2, var3)

def tseitin_transform_not(var1, var2):
    return '( ~{0} v ~{1} ) ^ ( {0} v {1} )'\
            .format(var1, var2)

def tseitin_transform_nand(var1, var2, var3):
    return '( ~{0} v ~{1} v ~{2} ) ^ ( {0} v {2} ) ^ ( {1} v {2} )'\
            .format(var1, var2, var3)

def tseitin_transform_nor(var1, var2, var3):
    return '( {0} v {1} v {2} ) ^ ( ~{0} v ~{2} ) ^ ( ~{1} v ~{2} )'\
            .format(var1, var2, var3)

def tseitin_transform_xor(var1, var2, var3):
    return '( ~{0} v ~{1} v ~{2} ) ^ ( {0} v {1} v ~{2} ) ^ ( {0} v ~{1} v {2} ) ^ ( ~{0} v {1} v {2} )'\
            .format(var1, var2, var3)

def tseitin_transform_xnor(var1, var2, var3):
    return '( {0} v {1} v {2} ) ^ ( ~{0} v ~{1} v {2} ) ^ ( ~{0} v {1} v ~{2} ) ^ ( {0} v ~{1} v ~{2} )'\
            .format(var1, var2, var3)

def tseitin_transform_implies(var1, var2, var3):
    return '( {0} v {1} v {2} ) ^ ( ~{0} v {1} v ~{2} ) ^ ( {0} v ~{1} v {2} ) ^ ( ~{0} v ~{1} v {2} )'\
            .format(var1, var2, var3)

def is_literal(term):
    if term.count('(') == 0 and term.count(')') == 0:
        return True
    if is_math_equation(term):
        return True
    return False

def is_math_equation(term):
    match = re.search(r'^\([^\(]+(<|<=|>=|[^-]>)[^/)]+\)$', term)
    if match:
        return True
    return False

def is_math_equality(term):
    match = re.search(r'^\([^\(]+[^!][=][^/)]+\)$', term)
    if match:
        return True
    return False

def is_math_not_equals(term):
    match = re.search(r'^\([^\(]+[!=][^/)]+\)$', term)
    if match:
        return True
    return False

def expand_equality(term):
    return '(and ' + term.replace('=', '<=') + ' ' + term.replace('=', '>=') + ')'

def expand_not_equals(term):
    x = '(or ' + term.replace('!=', '<') + ' ' + term.replace('!=', '>') + ')'
    return x


def convert_to_cnf(string):
    return add_to_cnf('', 'xi', string)

def add_to_cnf(current_cnf, output_variable, new_term):
    if is_math_equality(new_term):
        new_term = expand_equality(new_term)
    if is_math_not_equals(new_term):
        new_term = expand_not_equals(new_term)

    operator, left_term, right_term = None, None, None
    try:
        operator, left_term, right_term = \
                get_operator_and_variables_tuple(new_term)
    except(TypeError):
        fail('failed to parse term ' + str(new_term))
    #print left_term, '|', operator, '|', right_term
    if is_math_equation(left_term):
        left_term = get_associated_variable(left_term)
    # the stupid (not ...) operator creates so many freaking
    # corner cases
    if right_term and is_math_equation(right_term):
        right_term = get_associated_variable(right_term)

    left_var, right_var = left_term, right_term
    if not is_literal(left_term):
        if not current_cnf:
            current_cnf += \
                add_to_cnf(current_cnf, output_variable + 'L', left_term)
        else:
            current_cnf += ' ^ ' +\
                add_to_cnf(current_cnf, output_variable + 'L', left_term)
        left_var = output_variable + 'L'

    right_cnf = ''
    if right_term and not is_literal(right_term):
        if not right_cnf:
            right_cnf += \
                    add_to_cnf(right_cnf, output_variable + 'R', right_term)
        else:
            right_cnf += ' ^ ' +\
                    add_to_cnf(right_cnf, output_variable + 'R', right_term)
        right_var = output_variable + 'R'

    if right_cnf and current_cnf:
        current_cnf += ' ^ ' + right_cnf
    elif not current_cnf and right_cnf:
        current_cnf += right_cnf

    new_term_append = ''
    if current_cnf != '':
        new_term_append = ' ^ '
    if operator == 'and':
        current_cnf += new_term_append + \
                tseitin_transform_and(left_var, right_var, output_variable)
    elif operator == 'or':
        current_cnf += new_term_append + \
                tseitin_transform_or(left_var, right_var, output_variable)
    elif operator == 'not':
        current_cnf += new_term_append + \
                tseitin_transform_not(left_var, output_variable)
    elif operator == 'nand':
        current_cnf += new_term_append + \
                tseitin_transform_nand(left_var, right_var, output_variable)
    elif operator == 'nor':
        current_cnf += new_term_append + \
                tseitin_transform_nor(left_var, right_var, output_variable)
    elif operator == 'xor':
        current_cnf += new_term_append + \
                tseitin_transform_xor(left_var, right_var, output_variable)
    elif operator == 'xnor':
        current_cnf += new_term_append + \
                tseitin_transform_xnor(left_var, right_var, output_variable)
    elif operator == '->':
        current_cnf += new_term_append + \
                tseitin_transform_implies(left_var, right_var, output_variable)
    return current_cnf

def get_operator_and_variables_tuple(term):
    match = re.search(r'^\(({0}) (\w+|\(.+\))\)$'.format('not'), term)
    if match:
        return match.group(1), match.group(2), None
    operators = '|'.join(BOOL_OPERATORS)
    match = re.search(r'^\(({0}) (.+)\)$'.format(operators), term)
    if match:
        imbalanced = 0
        on_term_1 = True
        term1 = ''
        term2 = ''
        first_space = True
        terms = re.split('(\(|\)|\s)',match.group(2))
        terms = filter(lambda x: x != '', terms)
        for char in terms:
            if on_term_1:
                if char == '(':
                    imbalanced -= 1
                elif char == ')':
                    imbalanced += 1
                term1 += char
                if not imbalanced:
                    on_term_1 = False
            else:
                term2 += char

        return match.group(1),term1.strip(), term2.strip()

def dpll_to_simplex_interface(dict_var_to_eqn):
    # find all variables
    row_dict = {}
    col_dict = {}
    i = 0
    for key, eqn in dict_var_to_eqn.iteritems():
        row_dict[key] = i
        i = i + 1
        for key, val in eqn.left_hand_side.iteritems():
            col_dict[key] = 1
    # align variables
    i = 0
    for key in col_dict.keys():
        col_dict[key] = i
        i = i+1

    # build matrix inputs into simplex
    m = len(dict_var_to_eqn)
    n = len(col_dict)
    A = np.zeros((m,n), np.float32)
    b = np.zeros(m, np.float32)
    row = 0
    col = 0
    for key, eqn in dict_var_to_eqn.iteritems():
        if eqn.operator == "<=":
            for key, val in eqn.left_hand_side.iteritems():
                col = col_dict[key]
                A[row, col] = val
            b[row] = eqn.right_hand_side
        elif eqn.operator == ">=":
            for key, val in eqn.left_hand_side.iteritems():
                col = col_dict[key]
                A[row, col] = -val
            b[row] = eqn.right_hand_side

        row = row + 1

    return A, b, row_dict, col_dict

def convert_str_cnf_to_obj_cnf(str_cnf):
    ls_clauses = []
    str_clauses = str_cnf.split('^')
    for str_clause in str_clauses:
        ls_variables = re.split(' |\(|\)|v',str_clause)
        ls_variables = filter(lambda x: x != '', ls_variables)
        ls_clauses.append(dpll.Clause(ls_variables))
    return dpll.CNF_formula(ls_clauses)

def balanced_parens(str_input):
    imbalanced = 0
    for item in list(str_input):
        if item == '(':
            imbalanced -= 1
        elif item == ')':
            imbalanced += 1
    if imbalanced:
        return False
    return True

def parse_input(args):
    with open(args[1]) as ifile:
        str_input = ifile.read().replace('\n', '')

        if not balanced_parens(str_input):
            print "input does not have balanced parentheses"
            exit(1)

        cnf = convert_to_cnf(str_input)
        obj_cnf = convert_str_cnf_to_obj_cnf(cnf)
        global equation_dictionary
        dict_var_to_eqn = {}
        for key, val in equation_dictionary.iteritems():
            dict_var_to_eqn[val] = key
            dict_var_to_eqn['~'+val] = aa.negate_simplex(key)
        for key in dict_var_to_eqn:
            pass

        A, b, row_dict,col_dict = dpll_to_simplex_interface(dict_var_to_eqn)

        parsed_input = gv.ParsedInput(A, b, obj_cnf, row_dict, col_dict)
        return parsed_input
