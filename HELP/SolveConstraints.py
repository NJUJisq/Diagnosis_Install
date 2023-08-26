
from utils.version import Version,VersionError

def split(t_1):
    op = ''
    ver = ''
    for ch in t_1:
        if ch in ('>',"<","~","=",'!'):  #
            op = op + ch
        else:
            ver = ver + ch
    if op == '=':    
        op = '=='
    op = op.strip()
    ver = ver.strip().strip('.').strip(')').strip('(').strip('"').strip("'") 
    clean_ver = []
    ch_vers = ver.split('.')
    for chs in ch_vers:
        clean_chs = ''
        for ch in chs:
            if ch.isdigit() or ch in ['*','0']:   
                clean_chs += ch 
            else:
                
                break 
        
        clean_ver.append(clean_chs)

    
    clean_ver = '.'.join(clean_ver)
    if clean_ver == '3.1.0*':
        clean_ver == '3.10.*'

    return [op,clean_ver,ver]



class conflictNode(object):  
    def __init__(self,all_version,constraints):
        
        if isinstance(constraints,str):
            possible_vers = []
            self.constraints = self.transfer_constraint(constraints)  #
            for v in all_version:  
                if self.solve_constraint(v,self.constraints):
                    possible_vers.append(v)
            self.solved_versions = possible_vers
            
    def transfer_constraint(self,dep_self_versions):
        dep_self_constraints = []
        dep_self_versions = dep_self_versions.split(',')  
        for op_v in dep_self_versions:
            op,ver,org_ver = split(op_v)
            op = op.replace('\s','')  
            dep_self_constraints.append({'op':op,'ver':ver,'ori_ver':org_ver})  
        
        return dep_self_constraints


    def solve_versionNumber(self,v1,v2,mode=0):  
       
        version_num1 = v1.strip().split('.')
        version_num2 = v2.strip().split('.')

        if mode == 1:
            if '*' in version_num2: 
                version_num2.pop()  
            return version_num1,version_num2
        
        if '*' in version_num2: 
            version_num2.pop()  
        else:
            
            if len(version_num2) > len(version_num1):
                for i in range(len(version_num2) > len(version_num1)):
                    version_num1.append('0')
            if len(version_num1) > len(version_num2):
                for i in range(len(version_num1) > len(version_num2)):
                    version_num2.append('0') 
        
        return version_num1,version_num2
    
    def remove_pre(self,num):
        if isinstance(num,list):
            ver_new = ''
            for i in num:
                ver_new = ver_new + '.' + self.remove_pre(i)

            return ver_new.strip('.')

        if isinstance(num,str):
            ver = ''
            num = num.strip()   
            for ch in num:
                if ch.isnumeric():  
                    ver = ver + ch
                else:
                    break
            if len(ver) == 0:
                ver = '0'
            return ver

    def compute_versionNumber(self,v1,v2,op,ori_ver):  
       
        flag = True
        if op == '==':
            version_num1,version_num2 = self.solve_versionNumber(v1,v2)     
            for i,j in zip(version_num1,version_num2):
                if int(self.remove_pre(i)) != int(self.remove_pre(j)):  
                    flag = False
                    break
            if flag == True and v1==v2 and v2 != ori_ver:
                flag = False

        elif op == '!=': 
            '''
            != 1.1.*      # Same prefix, so 1.1.post1 does not match clause
            '''
            
            version_num1,version_num2 = self.solve_versionNumber(v1,v2)     
            for i,j in zip(version_num1,version_num2):
                if i != j:  
                    break
            else:
                flag = False


        elif op == '~=':  
            '''
            ~= 2.2  <==>    >= 2.2, == 2.*
            ~= 1.4.5  <==>     >= 1.4.5, == 1.4.*
            '''
            flag = self.compute_versionNumber(v1,v2,'>=',ori_ver)
            ver_withstar = v2.split('.')
            ver_withstar[-1] = '*'  
            ver_withstar = '.'.join(ver_withstar)
            version_num1,version_num2 = self.solve_versionNumber(v1,ver_withstar)     
            for i,j in zip(version_num1,version_num2):
                if i != j:  
                    flag = False
                    break
            

        elif op == '>=' or op == '>':
            try:
                version_num1,version_num2 = self.solve_versionNumber(v1,ori_ver,1)  
                version_1_norm = Version('.'.join(version_num1))
                version_2_norm = Version('.'.join(version_num2)) 
                
                if version_1_norm > version_2_norm:
                    if version_1_norm.compare_releases(version_1_norm._mmp(),version_2_norm._mmp()) == 'equal' and version_2_norm._mmp() != version_1_norm._mmp():   
                        if (version_2_norm.post == None and version_1_norm.post) or (version_2_norm.post and version_1_norm.post == None):
                            # print('filter post', version_1_norm)
                            return False 

                if version_1_norm < version_2_norm:   
                    flag = False
                if op == '>' and version_1_norm == version_2_norm:
                    flag = False

            except VersionError as e:
                flag = False  

        elif op == '<=' or op == '<':
            try:
                version_num1,version_num2 = self.solve_versionNumber(v1,ori_ver,1)  
                version_1_norm = Version('.'.join(version_num1))
                version_2_norm = Version('.'.join(version_num2))
                if version_1_norm < version_2_norm:

                    if version_1_norm.compare_releases(version_1_norm._mmp(),version_2_norm._mmp()) == 'equal' and version_2_norm._mmp() != version_1_norm._mmp():   
                        if (version_2_norm.pre_release == None and version_1_norm.pre_release) or (version_2_norm.pre_release and version_1_norm.pre_release == None):
                            return False  
                    
                if version_1_norm > version_2_norm:
                    flag = False
                if op == '<' and version_1_norm == version_2_norm:
                    flag = False

            except VersionError as e:
                flag = False
              
    
        return flag

    def solve_constraint(self,v1,contraints):
        
        
        flag = True
        for t in contraints: 
            flag = self.compute_versionNumber(v1,t['ver'],t['op'],t['ori_ver'])
            if flag == False: 
                break
        return flag


# test
# a = conflictNode(['0.1.1.post2207130030', '0.1.0.post220', '0.1.0', '0.1.1post220', '4.0.0rc3', '4.0.0rc4', '4.0.0rc5', '4.0.0rc6', '4.0.0'],
#             ">0.1.post2").solved_versions
# print(a)