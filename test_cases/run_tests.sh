#!/bin/bash
function assert ()
{
    if [[ $2 -eq 0 ]]
    then
        echo "$1... OK";
    else
        echo "$1... FAIL";
    fi
}

file="input_and"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="unsat_only_reals"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_less_than_zero"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_with_not"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_infeasible_mixed"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_fancier_equations"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_chained_gates"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_equals"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_strict_ineq"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_strict_ineq2"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_strict_ineq3"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_strict_ineq4"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_strict_ineq5"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_strict_ineq6"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_not_equal"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_not_equal2"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_not_not_eq"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_nand"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_nor"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_xor"
python ../smt_main.py $file | egrep '^unsat'
assert $file $?

file="input_xnor"
python ../smt_main.py $file | egrep '^sat'
assert $file $?

file="input_implies"
python ../smt_main.py $file | egrep '^sat'
assert $file $?
