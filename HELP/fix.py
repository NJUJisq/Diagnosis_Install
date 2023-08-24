

from z3 import Int, And, Or, simplify, Optimize
from create_csv_local import get_package_deps
from utils.sort_version import cmp_version
from functools import cmp_to_key
import time,json
from detect import run_one_detection


def build_order_dict(pkg_dict):
    order_dict = dict()
    int_dict = {}
    for pkg in pkg_dict:
        ver_dict = pkg_dict[pkg]
        order_dict[pkg] = dict()
        ind = 0
        int_dict[pkg] = Int(pkg)
        versions = list(ver_dict.keys())
        has_versions = []
        for v in versions:
            if v == 'False':
                pass
            else:
                has_versions.append(v)
        sorted_versions = sorted(has_versions, key=cmp_to_key(cmp_version)) 
        for ver_ in sorted_versions:
            order_dict[pkg][ver_] = ind
            ind += 1

    return int_dict,order_dict


def add_dependency_constrains(solver, pkg_dict, order_dict, int_dict,need_install):

    for pkg in pkg_dict:
        ver_dict = pkg_dict[pkg]
        ands = list()
        for ver in ver_dict:
            if ver == 'False':
                ands.append(And(False))  
                continue
            ind = order_dict[pkg][ver]
            
            deps = ver_dict[ver].copy()
            ors = list()
            smt_deps = {}
            for dep in deps:  
                dep_pkg, dep_ver = dep.split("#")
                if dep_pkg not in smt_deps:
                    smt_deps[dep_pkg] = []

                smt_deps[dep_pkg].append(dep_ver)

           
            
            for dep_pkg in smt_deps:
                expr1 = Or()
                if len(smt_deps[dep_pkg])==1 and smt_deps[dep_pkg][0] == 'True': 
                    for v_ in order_dict[dep_pkg]:
                        dep_ind = order_dict[dep_pkg][v_]
                        expr = Or(int_dict[dep_pkg]== dep_ind)
                        expr1 = Or(expr1,expr)
                        expr1 = simplify(expr1) 

                else:
                    for smt_ver in smt_deps[dep_pkg]:
                        if smt_ver == 'False': 
                            expr = Or(False)  #
                        elif smt_ver == 'True':  
                            print(dep_pkg,'------------')
                            continue  

                        else:
                            dep_ind = order_dict[dep_pkg][smt_ver]
                            expr = Or(int_dict[dep_pkg]== dep_ind)
                        expr1 = Or(expr1,expr)
                        expr1 = simplify(expr1)  
               

                ors.append(expr1)
            and_expr = And(int_dict[pkg] == ind)
            for expr in ors:
                and_expr = And(and_expr, expr)
                and_expr = simplify(and_expr)

            ands.append(and_expr)

    
        constrain = Or()
        for expr in ands:
            constrain = Or(constrain, expr)
            constrain = simplify(constrain)
 
        constrain = simplify(constrain)

        solver.add(constrain)
    return solver

def add_int_constrains(solver, pkg_dict, int_dict):
    for pkg in pkg_dict:
        ver_dict = pkg_dict[pkg]
        ver_len = len(ver_dict.keys())
        constrain = And(int_dict[pkg] >= 0, int_dict[pkg] <= ver_len)
        solver.add(constrain)
    return solver


def add_version_constrains(solver, constrain_version_dict, order_dict, int_dict):
    for pkg in constrain_version_dict:
        versions = constrain_version_dict[pkg]
        constrain = Or()
        for ver in versions:
            # print(pkg,ver)
            ind = order_dict[pkg][ver]
            if ind == 'False':
                constrain = Or(False)
            else:
                constrain = Or(constrain, int_dict[pkg] == ind)
            constrain = simplify(constrain)

        # print(constrain)
        solver.add(constrain)
    return solver


def add_optimize_targets(solver, int_dict):
    for pkg in int_dict:
        var = int_dict[pkg]
        solver.maximize(var)  
      
    return solver

def parse_z3_model(model, int_dict, order_dict):
    pkgvers = dict()
    object_s = 0
    for pkg in int_dict:
        var = int_dict[pkg]
        ver_ind = model[var]
        vers = [k for k, v in order_dict[pkg].items() if v == ver_ind] 

        if len(vers) == 0:
            continue  # ind = len(ver), unnecessary to install
        # elif len(vers) == 1 and vers[0] == 'False':  
        #     continue
        else:
            # print(pkg,len(vers))
            ver = vers[0]
            object_s += ver_ind
            
        pkgvers[pkg] = ver
    
    
    return pkgvers


def solving_constraints(pkg_dict, constrain_version_dict, need_install):
    solver = Optimize()
    int_dict,order_dict = build_order_dict(pkg_dict)
    solver = add_dependency_constrains(solver, pkg_dict, order_dict, int_dict,need_install)
    solver = add_int_constrains(solver, pkg_dict, int_dict)
    solver = add_version_constrains(solver, constrain_version_dict, order_dict, int_dict) 
    # solver = add_optimize_targets(solver, int_dict,constrain_version_dict)
    for pkg in int_dict:
        var = int_dict[pkg]
        solver.maximize(var)  

    try:
        if solver.check():
            pkgvers = parse_z3_model(solver.model(), int_dict, order_dict)
            return pkgvers
        else:
            return None
    except:
        return None


import copy
def solving_install_by_z3(pkgver_dict,need_install):
    c_dict = copy.deepcopy(pkgver_dict) 
    p_dict = get_package_deps(pkgver_dict)   
    res = solving_constraints(p_dict, c_dict, need_install)
    if res is None or "python" not in res:
        return None
    
    
    return res


def run_one(library,Sym,to_file=None):
    
    need_fix = True
    st = time.time()
    return_info = run_one_detection(library[0]+'#'+library[1],Sym,installed={})
    if return_info:
        temp_info,install_system_constraints,installed = return_info
        if temp_info.occur_level == 'level(1)' and temp_info.occur_type == 'CanNotFind':          # Incompatibility
            print('Install incompatibility in this Python version ')
            need_fix = False
        error_nodes = temp_info.error_nodes
        error_nodes.remove(library[0])
        has_installed = {}
        has_installed['python'] = {Sym}
        has_installed[library[0]] = [library[1]]
    else:
        if return_info == False:
            print('keyE')
        else:
            print('Can install ','#'.join(library)+'#'+Sym)
    
        need_fix = False
        
    if need_fix == False:
        et = time.time()
        detect_time = et-st
        print('time is',detect_time)
        return
    
    error_nodes = list(error_nodes)

    need_install = {}
    need_install[library[0]] = None
    for dep_order in reversed(error_nodes):  
        need_install[dep_order] = None

    
    py_pkgvers = solving_install_by_z3(has_installed,need_install)  
    
    et = time.time()
    run_time = et-st
    print('time is',run_time)

    if py_pkgvers:
        # print(library,Sym)
        fix_record = {}
        fix_record['pro#ver'] = library[0]+'#'+library[1]
        fix_record['Sym'] = Sym 
        fix_record['error'] = '('+temp_info.occur_type +')'+ error_nodes[-1]
        fix_record['error_fix'] = []
        fix_record['full_install'] = []
        fix_record['exeute_time'] = run_time
        for dep_order in reversed(error_nodes):  
            need_install[dep_order] = None
        for item in py_pkgvers:
            fix_record['full_install'].append(item+'=='+py_pkgvers[item])
            if item in error_nodes:
                need_install[item] = py_pkgvers[item]
                fix_record['error_fix'].append(item+'=='+py_pkgvers[item])

        # if to_file:
        #     with open(to_file,'w') as f:
        #         json.dump(fix_record,f,indent=4)
        with open('result/{}.json'.format(library[0]+'#'+library[1]+'#'+Sym),'w') as f:
            json.dump(fix_record,f,indent=4)
    else:
        print('HELP fails to generate a solution for this installation task')
    # return need_install,detect_time


def norm(s):
    return s.lower().replace('-','_') 

import sys
def main():

    tmp = sys.argv[1]
    tmp = tmp.split('#')
    library = (norm(tmp[0]),tmp[1])

    Sym = tmp[2]
    
    print('#'.join(library)+'#'+Sym)
    run_one(library,Sym)
    
    

        
if __name__ == '__main__':
    main()

