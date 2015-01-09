==================== RUN SMT ====================

python smt_main.py input_file

==================== RUN DIMACS SAT ====================

python dpll.py dimacs_file

These files are in the cnf folders and were downloaded from
the dimacs website. Solving can take up to 20 seconds on a
fast laptop (Intel i7 Ivy Bridge, linux in vmware)

The unsatisfiable instances take around 60 seconds to solve.

==================== SMT FILE FORMAT TL;DR ====================
Check the test_cases directory to see what input looks like

==================== SMT FILE FORMAT ====================
(bool_op (term) [term])

bool_op     = (and|or|not|nand|nor|xor|xnor|->)

term        = (bool_op (term) [term])
            = equation
            = boolean_var

equation    = expression (math_op) expression

math_op     = (!=, =, >=, <=, >, <)

expression  = arith_term [arith_op expression]
            = real 

arith_op    = (+, -)

arith_term  = real
            = [real][*]real_variable

Variables can be of the format [a-z]+[0-9]+ but cannot use the reserved
characters (v, q, p, sat)

You do not need to specify if a variable is boolean or real. This is
determined from the context.

Math equations may only use addition and subtraction. Multiplication is only
allowed between coefficients and variables. E.g.

Legal:

-3*a2 + 4a3 < 8a1 - 2*a2

Illegal:
a1*a2 < a3

It is legal to do identically true equations like (1 = 1). However idetically
false equations like (1 = 2) leads to undefined behavior.

