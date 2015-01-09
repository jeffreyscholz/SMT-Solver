import sys
import parse as pl
import global_vars as gv
import dpll as dpll

def display_result(ret, real_sol):
    removed_intermediate_variables = {}
    if not ret:
        print 'unsat'
    else:
        print 'sat'
        for var in ret:
            if 'q' not in var and 'xi' not in var:
                removed_intermediate_variables[var] = ret[var]
        if removed_intermediate_variables:
            print removed_intermediate_variables
        if real_sol:
            for key in real_sol:
                print str(key), '=', str(real_sol[key])

def main(args):
    if len(args) < 2:
        pl.fail('usage: python {0} input_file'.format(args[0]))
    parsed_input = pl.parse_input(args)
    solver = dpll.CNF_formula_helpers()
    sat_assignment, real_sol = solver.dpll(parsed_input.cnf, parsed_input)
    display_result(sat_assignment, real_sol)

if __name__ == '__main__':
    main(sys.argv)
