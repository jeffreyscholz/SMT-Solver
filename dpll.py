import copy, random, sys
from collections import defaultdict
from simplex_init_only import Simplex

class ClauseConflictException(Exception):
    pass

class CNF_formula_helpers:
    def __init__(self):
        self.mySimplex = None

    def simplex_feasible(self, assignment, parsed_input):
        if parsed_input == 'dimacs':
            return True
        equation_variables = {}
        rows = []
        for var in assignment:
            if 'q' in var:
                equation_variables[var] = assignment[var]
                #print 'var',var, equation_variables[var]
                if equation_variables[var]:
                    rows.append(parsed_input.row_dict[var])
                else:
                    rows.append(parsed_input.row_dict['~'+var])



        #print rows
        '''
        if len(rows) <= 1:
            return True
        else:
        '''
        #print parsed_input.A, parsed_input.b, rows

        #mySimplex = Simplex(parsed_input.A, parsed_input.b,rows)
        self.mySimplex = Simplex(parsed_input,rows)
        if self.mySimplex.solve():
            return self.mySimplex
        else:
            return False
        #return mySimplex.solve()
    def simplex_result(self, mySimplex, assignment, parsed_input):
        return mySimplex.get_assignment()

    def dpll(self, cnf_formula, parsed_input):
        unpicked_variables = cnf_formula.get_set_variables()
        #set initial clause indexes
        top_level_assignmentTree = []
        if 'xi' in unpicked_variables:
            top_level_assignmentTree = [{'xi': [{'xi': True}]}]
        counter = 0
        for clause in cnf_formula.ls_clauses:
            clause.clause_index = counter
            counter += 1
        ret = self.dpll_recursive2(cnf_formula, top_level_assignmentTree, unpicked_variables, parsed_input)
        while isinstance(ret,list):
            new_clause = ret[0]
            new_clause.clause_index = len(cnf_formula.ls_clauses)
            cnf_formula.ls_clauses.append(new_clause)
            #recursive call itself
            unpicked_variables = cnf_formula.get_set_variables()
            ret = self.dpll_recursive2(cnf_formula, top_level_assignmentTree, unpicked_variables, parsed_input)

        real_sol = None
        if ret != False and self.mySimplex != None:
            #print 'result',self.simplex_result(ret,mySimplex, parsed_input)
            #print 'solution:'
            real_sol = self.mySimplex.get_assignment()
        return ret, real_sol


    def dpll_recursive2(self, cnf_formula, assignmentTree, unpicked_variables, parsed_input):
        #reconstruct the assignment list
        assignments = {}
        nodes = {}
        counter = 0
        for dictionary in assignmentTree:
            for key,value in dictionary.iteritems():
                nodes[key] = counter
                counter += 1
                for assign in value:
                    assignments.update(assign)
        current_level_cnf_formula = copy.deepcopy(cnf_formula)
        current_level_cnf_formula = self.simplify(current_level_cnf_formula, assignments)
        if current_level_cnf_formula.assign(assignments):
            return assignments
        elif current_level_cnf_formula.has_empty_clause():
            return False
        else:
            #choice_var_raw = current_level_cnf_formula.find_next_variable()
            choice_var_raw = current_level_cnf_formula.highest_frequent_variable()
            choice_var = choice_var_raw
            if "~" in choice_var_raw:
                choice_var = choice_var_raw.replace("~", "")

            unpicked_variables.remove(choice_var)

            for var_assignment in [False, True]:
                #set choice_var to be correct value
                old_assignmentTree = copy.deepcopy(assignmentTree)
                if choice_var == choice_var_raw:
                    choice_of_assignment = {choice_var : var_assignment}
                else:
                    choice_of_assignment = {choice_var : not var_assignment}
                assignmentList = [choice_of_assignment]
                #add choice of assignment into assignment list
                assignments.update(choice_of_assignment)
                if self.simplex_feasible(assignments, parsed_input) == False:
                    continue

                test_cnf_formula = copy.deepcopy(current_level_cnf_formula)
                simplified_cnf_formula = self.simplify(test_cnf_formula, assignments)
                if simplified_cnf_formula.has_empty_clause():
                    #print "empty clause right after assignment"
                    continue

                merged_assignments = copy.deepcopy(assignments)
                remaining_variables = simplified_cnf_formula.get_set_variables()
                unit_assignments = self.get_unit_clauses_assignments(simplified_cnf_formula)

                while (unit_assignments):
                    #print "unit_assignments",unit_assignments
                    if "Error" in unit_assignments:
                        #print "conflict between clauses",unit_assignments["Error"][0],unit_assignments["Error"][1],len(cnf_formula.ls_clauses)
                        #add new clause to cnf_formula
                        alpha = unit_assignments["Error"][0]
                        beta = unit_assignments["Error"][1]
                        conflict_variable = unit_assignments["Error"][2]
                        clause_alpha = None
                        clause_beta = None
                        #might need following line
                        #current_level_cnf_formula = self.simplify(current_level_cnf_formula, assignments)
                        for clause in cnf_formula.ls_clauses:
                            if clause.clause_index == alpha:
                                clause_alpha = clause
                            if clause.clause_index == beta:
                                clause_beta = clause
                                break
                        new_clause_variables = []
                        for variable in clause_alpha.ls_variables:
                            var = variable
                            if self.is_negated(variable):
                                var = self.strip_negation(variable)
                            if var != conflict_variable:
                                new_clause_variables.append(variable)
                        for variable in clause_beta.ls_variables:
                            var = variable
                            if self.is_negated(variable):
                                var = self.strip_negation(variable)
                            if var != conflict_variable and variable not in new_clause_variables:
                                new_clause_variables.append(variable)
                        new_clause = Clause(new_clause_variables)
                        #print clause_alpha.ls_variables, clause_beta.ls_variables
                        #print new_clause.ls_variables
                        go_up_to = None
                        for var_raw in new_clause.ls_variables:
                            var = var_raw
                            if "~" in var_raw:
                                var_raw = var_raw.replace("~", "")
                            if var_raw in nodes:
                                if go_up_to is None:
                                    go_up_to = nodes[var_raw]
                                elif nodes[var_raw] < go_up_to:
                                    go_up_to = nodes[var_raw]
                        if go_up_to is None:
                            return [new_clause,None]
                        else:
                            return_target = "origin"
                            go_up_to -= 1
                            if go_up_to >= 0:
                                node_dict = assignmentTree[go_up_to]
                                for key,value in node_dict.iteritems():
                                    return_target = key
                            #print "return to",return_target
                            return [new_clause,return_target]
                    else:
                        try:
                            merged_assignments = self.merge_assignments(unit_assignments, merged_assignments)
                        except(ClauseConflictException):
                            break
                        if self.simplex_feasible(merged_assignments, parsed_input) == False:
                            break
                        simplified_cnf_formula = self.simplify(simplified_cnf_formula, merged_assignments)
                        if simplified_cnf_formula.has_empty_clause():
                            #print "empty clause after unit_clause"
                            break
                        remaining_variables = simplified_cnf_formula.get_set_variables()

                        for key,value in unit_assignments.iteritems():
                            assignmentList.append({key : value})
                        unit_assignments = self.get_unit_clauses_assignments(simplified_cnf_formula)

                if self.simplex_feasible(merged_assignments, parsed_input) == False:
                    continue
                if simplified_cnf_formula.has_empty_clause():
                    #print "continue on same level"
                    continue

                old_assignmentTree.append({choice_var : assignmentList})
                ret = self.dpll_recursive2(cnf_formula, old_assignmentTree, remaining_variables, parsed_input)
                while isinstance(ret,list):
                    if ret[1] is None:
                        new_clause = ret[0]
                        new_clause.clause_index = len(cnf_formula.ls_clauses)
                        cnf_formula.ls_clauses.append(new_clause)
                        unpicked_variables = current_level_cnf_formula.get_set_variables()
                        ret = self.dpll_recursive2(cnf_formula, old_assignmentTree, unpicked_variables, parsed_input)
                    else:
                        if choice_var == ret[1]:
                            new_clause = ret[0]
                            new_clause.clause_index = len(cnf_formula.ls_clauses)
                            cnf_formula.ls_clauses.append(new_clause)
                            #recursive call itself
                            unpicked_variables = current_level_cnf_formula.get_set_variables()
                            old_assignmentTree = copy.deepcopy(assignmentTree)
                            ret = self.dpll_recursive2(cnf_formula, old_assignmentTree, unpicked_variables,parsed_input)
                        else:
                            return ret
                if ret:
                    return ret
            #print "return previous level from",choice_var
            return False

    def simplify(self, cnf_formula, assignment):
        ls_simplified_cnf_clauses = []
        for clause in cnf_formula.ls_clauses:
            if not clause.assign(assignment):
                clause = self.remove_false_variables(clause, assignment)
                ls_simplified_cnf_clauses.append(clause)

        ret = CNF_formula(ls_simplified_cnf_clauses)
        return ret

    def remove_false_variables(self, clause, assignment):
        for var, value in assignment.iteritems():
            if var in clause.ls_variables and value == False:
                clause.remove(var)
            if self.negate(var) in clause.ls_variables and value == True:
                clause.remove(self.negate(var))
        return clause

    def get_unit_clauses_assignments(self, cnf_unit_clauses):
        new_assignments = {}
        clause_track = {}
        for unit_c in cnf_unit_clauses.ls_clauses:
            if len(unit_c.ls_variables) == 1:
                var = unit_c.ls_variables[0]
                assignment = True
                if self.is_negated(var):
                    assignment = False
                var_identifier = self.strip_negation(var)
                if var_identifier in new_assignments:
                    if new_assignments[var_identifier] != assignment:
                        #set None to conflict variable
                        new_assignments["Error"] = [clause_track[var_identifier],unit_c.clause_index,var_identifier]
                        break
                else:
                    new_assignments[var_identifier] = assignment
                    clause_track[var_identifier] = unit_c.clause_index
        return new_assignments

    def get_assignments_from_unit_clauses(self, cnf_unit_clauses):
        new_assignments = {}
        for unit_c in cnf_unit_clauses.ls_clauses:
            if len(unit_c.ls_variables) == 1:
                var = unit_c.ls_variables[0]
                assignment = True
                if self.is_negated(var):
                    assignment = False
                var_identifier = self.strip_negation(var)
                if var_identifier in new_assignments and new_assignments[var_identifier] != assignment:
                    raise ClauseConflictException()
                new_assignments[var_identifier] = assignment
        return new_assignments

    def is_negated(self, variable):
        return '~' in variable

    def negate(self, variable):
        return '~' + variable

    def strip_negation(self, variable):
        return variable.replace("~", "")

    def has_assignment_conflict(self, assignment_1, assignment_2):
        intersection = assignment_1.viewkeys() & assignment_2.viewkeys()
        for key in intersection:
            if assignment_1[key] != assignment_2[key]:
                return True
        return False

    def merge_assignments(self, assignment_1, assignment_2):
        if self.has_assignment_conflict(assignment_1, assignment_2):
            raise ClauseConflictException()
        else:
            a = copy.deepcopy(assignment_1)
            a.update(assignment_2)
            return a

class CNF_formula:
    def __init__(self, ls_clauses):
        self.ls_clauses = ls_clauses

    def __str__(self):
        output = ''
        for clause in self.ls_clauses:
            output += str(clause.ls_variables)
        return output

    def get_set_variables(self):
        variables = set()
        for clause in self.ls_clauses:
            for var in clause.ls_variables:
                if "~" in var:
                    var = var.replace("~", "")
                variables.add(var)
        return variables

    def find_next_variable(self):
        for clause in self.ls_clauses:
            for var in clause.ls_variables:
                return var

    def highest_frequent_variable(self):
        dict_counts = {}
        for clause in self.ls_clauses:
            for var in clause.ls_variables:
                if "~" in var:
                    var = var.replace("~", "")
                if var in dict_counts:
                    dict_counts[var] += 1
                else:
                    dict_counts[var] = 1
        max_count = 0
        max_variable = ""
        for key,val in dict_counts.iteritems():
            if val > max_count:
                max_count = val
                max_variable = key
        return max_variable

    def assign(self, dict_assignments):
        for clause in self.ls_clauses:
            if not clause.assign(dict_assignments):
                return False
        return True

    def has_empty_clause(self):
        return len(filter(lambda clause: 0 == len(clause.ls_variables), self.ls_clauses)) >= 1

    def unit_clauses(self):
        return filter(lambda clause: len(clause.ls_variables) == 1, self.ls_clauses)

class Clause:
    # expect in form [x1, x2', x3]
    def __init__(self, ls_variables):
        self.ls_variables = ls_variables
        #extra paramter to locate clause index
        self.clause_index = 0

    # expect in form {x1: True, x2: False, x3: False}
    def assign(self, dict_assignments):
        for var in self.ls_variables:
            not_negated = True
            var_index = var
            if "~" in var:
                not_negated = False
                var_index = var.replace("~", "")
            if var_index in dict_assignments:
                if not_negated == dict_assignments[var_index]:
                    return True
        return False

    def remove(self, var):
        self.ls_variables.remove(var)

def main():
    if len(sys.argv) < 2:
        print 'usage: python {0} dimacs_sat_file'.format(sys.argv[0])
        exit(1)
    helper = CNF_formula_helpers()
    clauses = []
    with open(sys.argv[1]) as f:
        for line in f:
            if line and len(line.split()) >= 3:
                ls_line = line.split()
                if ls_line[0] != 'c' and ls_line[0] != 'p':
                    clause = []
                    for var in ls_line[0:3]:
                        if '-' in var:
                            var = var.replace('-', '')
                            var = '~x'+var
                        else:
                            var = 'x'+var
                        clause.append(var)
                    clauses.append(clause)
        f.close()

    ls_clause_objs = []
    for clause in clauses:
        clause_obj = Clause(clause)
        ls_clause_objs.append(clause_obj)
    cnf_f = CNF_formula(ls_clause_objs)
    sat_assign = helper.dpll(cnf_f, 'dimacs')
    print sat_assign[0]
    #print cnf_f.assign(sat_assign[0])

if __name__ == '__main__':
    main()
