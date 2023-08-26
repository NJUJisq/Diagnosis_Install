
import functools
from get_data import get_pkgver_by_pkg,get_deps_by_pkgver,get_pyvers_by_pkgver,get_pkg_label
from utils.sort_version import cmp_version_reverse,py_install_versions



class dependencyconflictException(Exception): #dependency conflict
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

class systemconflictException(Exception):  #incompatibility
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

from get_data import isvalid_req

from SolveConstraints import conflictNode
from utils.version import Version

def is_stable(ver):
    ver_ = Version(ver)
    if ver_.pre_release or ver_.post or ver_.dev or ver_.local:
        return False
    return True 

def run_one_detection(client,Sym,installed=None):

    
    if installed == None:
        installed = {}
    install_orders = [client]
    installed[client.split('#')[0]] = client
    
    Final_deps = {}
    best_deps = {}
    install_system_constraints= {}

    install_system_constraints[client.split('#')[0]] = {'name':client.split('#')[0],'install_v':client,'upper':'*'}
    
    level = 1
    while len(install_orders) > 0:
        install_new = []  
        
        for client_pkgver in install_orders:
            if not client_pkgver.isdigit() or isinstance(client_pkgver,int):
                try:
                    client_id = get_pkg_label(client_pkgver)  
                except KeyError as e:
                    return False
            
            try:
                possible_deps = get_deps_by_pkgver(client_id) 
            except KeyError as e:
                
                # incomplete knowledge base
                if client_pkgver in cache_nographs:
                    pass
                else:
                    cache_nographs.append(client_pkgver)
                    # with open('Nograph.txt','a') as f:
                    #     f.write(client_pkgver+'\n')
                return   
            if possible_deps == False:
                possible_deps = []
            
            same_level_deps = []  #
            for dep in possible_deps: 
                
                
                flag_valid,remove_cons = isvalid_req(client_pkgver,dep,Sym)
                if flag_valid == False:
                    
                    continue
                
                
                dep_cons = possible_deps[dep]
                if len(remove_cons) > 0:
                    for r_con in remove_cons:
                        r_con= r_con.strip(')').strip(',')  
                        dep_cons = dep_cons.replace(r_con,'',1)
                    
                dep_cons = dep_cons.strip().strip(',')  

                dep_all_version = get_pkgver_by_pkg(dep)  
                # print(dep_all_version)
                vers = conflictNode(list(dep_all_version),dep_cons).solved_versions  


                vers.sort(key=functools.cmp_to_key(cmp_version_reverse))  
                # if len(vers) == 0:  
                #     with open('temp_2.txt','a') as f:
                #         f.write(','.join([client_pkgver,dep,dep_cons])+'\n')
                    
                Final_deps[dep] = []  
                best_deps[dep] = False
                order_dep = {}
                order_label = 1
                for item in vers:
                    order_dep[dep+'#'+item] = order_label
                    order_label += 1
                
                
                for ver in vers: 
                    pv_info = dep+'#'+ver
                    
                    if pv_info not in cache_LC:                            
                        possible_pyvers =  get_pyvers_by_pkgver(pv_info,Empirical_install_versions)
                        # print(possible_pyvers)
                        
                        cache_LC[pv_info] = possible_pyvers
                        # cache_Interpreter[info] = dep_info[info]['interpreter']
                        # cache_Platform[info] = dep_info[info]['platform']
                    else:
                        possible_pyvers = cache_LC[pv_info]

                    if Sym in possible_pyvers:
                        Final_deps[dep].append(pv_info)  

                if len(Final_deps[dep]) > 0 :
                    tmp_dep = Final_deps[dep][0]  
                    stable_dep = None 
                    if is_stable(tmp_dep.split('#')[1]):
                        stable_dep = tmp_dep.strip()

                    for tmp in Final_deps[dep]:
                        if  order_dep[tmp] < order_dep[tmp_dep]:  #
                            
                            tmp_dep = str(tmp)

                        if is_stable(tmp.split('#')[1]):
                            if stable_dep == None:
                                stable_dep = str(tmp)
                            else:
                                if order_dep[tmp] < order_dep[stable_dep]:
                                    stable_dep = str(tmp)
                        
                    # choose the stable version
                    if stable_dep:
                        best_deps[dep] = stable_dep
                    else:
                        best_deps[dep] = tmp_dep

                if dep in installed:
                    
                    if installed[dep] in Final_deps[dep]:  
                        pass
                        
                    else:
                        if dep in same_level_deps:
                            pass
                        else:
                            from conflictcase_parse import ConflictCase
                            install_system_constraints['VC_2'] = {'name':dep,'install_v':'Unknown','upper':client_pkgver.split('#')[0]}
                            temp = ConflictCase('level({})'.format(level),'DependencyConflict',client.split('#')[0],client.split('#')[1],dep,Sym)
                            temp.parse_chain(install_system_constraints,dep)
                            print('detect error: level({}) dependency conflict for {} {} in python {}'.format(level,dep,installed[dep],Sym))
                            return temp,install_system_constraints,installed
   
                else:
                    
                    if best_deps[dep]:  
                        installed[dep] = best_deps[dep]
                        install_new.append(best_deps[dep])
                
                    else: 
                        from conflictcase_parse import ConflictCase
                        install_system_constraints[dep] = {'name':dep,'install_v':'Unknown','upper':client_pkgver.split('#')[0]}
                        temp = ConflictCase('level({})'.format(level),'CanNotFind',client.split('#')[0],client.split('#')[1],dep,Sym)
                        temp.parse_chain(install_system_constraints,dep)
                        
                        print('detect error: level({}) cannot find a version for {} in python {}'.format(level,dep,Sym))
                        return temp,install_system_constraints,installed

                        

                    install_system_constraints[dep] = {'name':dep,'install_v':installed[dep],'upper':client_pkgver.split('#')[0]}

                    same_level_deps.append(dep)
                    
                    
        
        install_orders = install_new.copy()
        level += 1
        
    print('{}=={} can be successfully installed in Python=={}'.format(client.split('#')[0],client.split('#')[1],Sym))
        
 

All_dep_info = {}
cache_LC = {}  
cache_Interpreter = {}
cache_Platform = {}
cache_nographs = []

Empirical_install_versions =  py_install_versions



#test
# run_one_detection('cmreshandler#1.0.0','3.9.2')   #hcai_nova_server 0.1.14 3.6.5
