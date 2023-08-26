
from SolveConstraints import conflictNode
from utils.sort_version import cmp_version_reverse,py_install_versions
import gzip
import os
import json
import functools


current_folder = "data/"

contain_SC = {}

with open('data/contain_SC.txt','r',encoding='utf-8') as fr:
    lines = fr.readlines()
    for line in lines:
        line = line.split('\t')
        # print(line)
        if len(line) == 2:
            continue
        pkgver = os.path.splitext(line[0])[0]
        pkgver = pkgver.lower().replace('-','_')
        if pkgver not in contain_SC:
            contain_SC[pkgver] = {}
        
        if line[1].strip() not in contain_SC[pkgver]:
            contain_SC[pkgver][line[1].strip()] = [] 
            
        contain_SC[pkgver][line[1].strip()].append({'cons':line[2],'env':line[3].strip()}) #可能有多个

def read_gzip_file_to_json(gzip_file_path):
    with gzip.open(gzip_file_path, 'rt', encoding='UTF-8') as zipfile:
        json_data = json.load(zipfile)
        return json_data
    
def reverse_labels(labels):
    res = {}
    pos = {}
    for k,vs in labels.items():
        for v in vs:
            res[str(vs[v])] = k+'#'+v 
            pos[k+'#'+v ] = str(vs[v])
    return pos,res


labels = read_gzip_file_to_json(current_folder+'labels.shrink')
deps = read_gzip_file_to_json(current_folder+'deps.shrink')
python_cons = read_gzip_file_to_json(current_folder+'LCs.shrink')
labels_one_to_one,labels_to_pkgver = reverse_labels(labels)

    
pkgVers_cache = {}
def get_pkgver_by_pkg(pkg):
    # pkg_id = get_pkg_label(pkg)
    if pkgVers_cache.__contains__(pkg):
        package_data = pkgVers_cache[pkg]
        if 'error' in package_data:
            return {}
        return package_data
    else:
        versions = list(labels[pkg].keys())
        pkgVers_cache[pkg] = versions

        return versions
    

labels_id_cache = {}
def get_pkg_label(pkgver):
    if labels_id_cache.__contains__(pkgver):
        package_data = labels_id_cache[pkgver]
        if package_data == 'error':
            return {}
        return package_data
    else:
        package_id = labels_one_to_one[pkgver]
        labels_id_cache[pkgver] = package_id     

        return package_id
        

deps_cache = {}


def get_deps_by_pkgver(pkgver):
    pkg_id = pkgver
    
    if deps_cache.__contains__(pkg_id):  
        package_data = deps_cache[pkg_id]
        if 'error' in package_data:
            return {}
        return package_data
    else:
        if 1:
            dependency_data = deps[str(pkg_id)]
      
        if dependency_data == '0':
            dependency_data = {}

        translated_dependencies = {}
        for item in dependency_data:
            id_to_pkg = labels_to_pkgver[item].split('#')[0]  
            translated_dependencies[id_to_pkg] = dependency_data[item]
       
        deps_cache[pkg_id] = translated_dependencies

        return translated_dependencies  


pycons_cache = {}

def get_pyvers_by_pkgver(pkgver,python_all_versions):
    try:
        pkg_id = get_pkg_label(pkgver)
    except KeyError:
        return []

    if pycons_cache.__contains__(pkg_id):
        return pycons_cache[pkg_id]
    else:
        try:
            package_pvs = python_cons[str(pkg_id)]     
            if len(package_pvs) == 0:
                package_pvs = ''
            else:
                package_pvs = package_pvs.replace('#',',')
        except KeyError:
            package_pvs = ''
        if len(package_pvs) > 0:
            solved_versions = conflictNode(python_all_versions,package_pvs).solved_versions
        else:
            solved_versions = python_all_versions
        pycons_cache[pkg_id] = solved_versions

        return solved_versions
        


def remove_unstable(vers):
    
    new_vers = set()
    for ver_ in vers:
        stable = 1
        for ch in ver_:
            if ch.isdigit() or ch == '.' or ch == '0':
                pass
            else:
                stable = 0
                break
        if stable == 0:
            continue  
        new_vers.add(str(ver_))  
    return list(new_vers)



def isvalid_req(pkg,req,sym):
    '''
    remove invalid dependency requirements according to the local Python version
    '''
    remove_cons = []
    if pkg in contain_SC:
        if req in contain_SC[pkg]:
            for condition in contain_SC[pkg][req]:
                env = condition['env']
                if 'python_version' not in env:  
                    remove_cons.append(condition['cons'])
                  
                else:
                    items = env.split('and')
                    scs = []
                    for item in items:
                        
                        if  'python_version' in item:
                            c = item.replace('python_version','').replace('\"','"').replace("\'","'")  
                       
                            if 'not in' in c:
                                scs.append(c.replace('not in','!=').strip())
                            elif 'in' in c:
                                scs.append(c.replace('in','==').strip())
                            elif '>' in c or '<' in c:  #先这样吧
                                
                                scs.append(c.strip())
                    
                    if len(scs) == 0:
                        
                        remove_cons.append(condition['cons'])
                        continue
                    tmp_r = conflictNode([sym],','.join(scs)).solved_versions
                    if len(tmp_r) == 0:
                        
                        remove_cons.append(condition['cons'])
                       
            if len(remove_cons) == len(contain_SC[pkg][req]):
                return False,remove_cons
            if len(remove_cons) < len(contain_SC[pkg][req]):
                return True, remove_cons
                
    else:
        return True,remove_cons
    
    return True,remove_cons

cache_solves = {}  
cache_flags = {}
def get_package_deps(pkgvers):
    pkg_dict = dict()    
    from queue import Queue
    queue = Queue()
    for pkgmth in pkgvers:
        pkg = pkgmth
        
        vers = pkgvers[pkgmth]
        for ver in vers:
            pkgver = "{}#{}".format(pkg, ver)
            queue.put(pkgver)


    while queue.qsize() > 0:
        pkgver = queue.get()
        pkg, ver = pkgver.split("#")[:2]
        
        
        if pkg not in pkg_dict:
            pkg_dict[pkg] = dict()
        if ver in pkg_dict[pkg]:
            continue
        
       
        pkg_dict[pkg][ver] = list()

        if pkg == 'python':
            sym = list(pkgvers[pkg])[0]
            continue

        if ver == 'False':
            continue
        
        try:
            related = get_deps_by_pkgver(get_pkg_label(pkg+'#'+ver))  
        except KeyError:
            continue

        for dep_pkgver in related: 
            flag_valid ,remove_cons= isvalid_req(pkg+'#'+ver,dep_pkgver,sym)
            if flag_valid == False:    
                continue
                        
            dep_cons = related[dep_pkgver]
            if len(remove_cons) > 0:
                for r_con in remove_cons:
                    r_con= r_con.strip(')').strip(',')  
                    dep_cons = dep_cons.replace(r_con,'',1)
                
            dep_cons = dep_cons.strip().strip(',')

            no_cons_flag = False
            if dep_pkgver + dep_cons+sym in cache_solves:
                compatible_versions = cache_solves[dep_pkgver + dep_cons+sym]  
                no_cons_flag = cache_flags[dep_pkgver + dep_cons+sym]
            else:
                dep_all_version = get_pkgver_by_pkg(dep_pkgver)
            
                temp_vers = conflictNode(remove_unstable(dep_all_version),dep_cons).solved_versions  
            
                if len(temp_vers) == len(dep_all_version):
                    no_cons_flag = True
                    # queue.put(dep_pkgver+'#True')  
                    # continue
                
                cache_flags[dep_pkgver + dep_cons+sym] = no_cons_flag
                compatible_versions = []
                for temp_v in temp_vers:
                    pyvers_cons = get_pyvers_by_pkgver(dep_pkgver+'#'+temp_v,py_install_versions)
                    if sym not in pyvers_cons:
                        continue
                    compatible_versions.append(temp_v)

                if len(compatible_versions) == 0:  
                    pkg_dict[pkg][ver].append(dep_pkgver+'#False') 
                    queue.put(dep_pkgver+'#False') 
                    continue
                
                

                compatible_versions = sorted(compatible_versions,key=functools.cmp_to_key(cmp_version_reverse))  
                if len(compatible_versions) <= 20:  
                    pass
                else:
                    compatible_versions = compatible_versions[0:20]  

                # if the number of versions is more than 20, HELP removes the unstable versions.
                # if len(compatible_versions) > 20: 
                #     compatible_versions = list(remove_unstable(compatible_versions)) 

                cache_solves[dep_pkgver + dep_cons+sym] = compatible_versions               
          
            # if no_cons_flag:
            #     pkg_dict[pkg][ver].append(dep_pkgver+'#True') 

            for temp_v in compatible_versions:
                pkg_dict[pkg][ver].append(dep_pkgver+'#'+temp_v) 

                queue.put(dep_pkgver+'#'+temp_v)

    return pkg_dict

