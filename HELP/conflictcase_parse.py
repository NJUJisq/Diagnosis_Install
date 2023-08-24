class ConflictCase(object):  
    
    def __init__(self,occur_level,occur_type,client_name,client_version,name,Sym):
        self.occur_level = occur_level  
        self.occur_type = occur_type  
        self.client_name = client_name
        self.client_version = client_version
        self.name = name
        self.Sym = Sym
        self.chain = ''      
    def Find_rootcause(self): 
        install_system_constraints = []
    def parse_chain(self,install_system_constraints,dep_now='*'): 
        if self.occur_type == 'CanNotFind':
            str_ = ''
            last_dep = dep_now  
            error_nodes = {last_dep}
            while(1):
                if last_dep == '*':
                    break
                if last_dep in install_system_constraints: 
                    error_nodes.add(install_system_constraints[last_dep]['name'])
                    str_ += install_system_constraints[last_dep]['name']+'['+ install_system_constraints[last_dep]['install_v'] + ']<--'  
                    last_dep = install_system_constraints[last_dep]['upper']

            print(str_)
            self.chain = str_
            self.error_nodes = error_nodes
        if self.occur_type == 'DependencyConflict':

            chains_long = ''
            last_dep = 'VC_2'  
            error_nodes = set()
            len_ = 1
            while(1):
                if last_dep == '*':
                    break
                if len_ == 10:  
                    chains_long += '[hugeerror]<--'  
                    break
                if last_dep in install_system_constraints: 
                    error_nodes.add(install_system_constraints[last_dep]['name'])
                    chains_long += install_system_constraints[last_dep]['name']+'['+ install_system_constraints[last_dep]['install_v'] + ']<--'  
                    last_dep = install_system_constraints[last_dep]['upper']
                    
                len_ += 1

            len_ = 1
            chains_short = ''
            last_dep = dep_now  
            error_nodes.add(last_dep)
            while(1):
                if last_dep == '*':
                    break
                if len_ == 10:  
                    chains_long += '[hugeerror]<--'  
                    break
                if last_dep in install_system_constraints: 
                    error_nodes.add(install_system_constraints[last_dep]['name'])
                    chains_short += install_system_constraints[last_dep]['name']+'['+ install_system_constraints[last_dep]['install_v'] + ']<--'  
                    last_dep = install_system_constraints[last_dep]['upper']
                    
                len_ += 1

            self.chain = chains_long + '#' + chains_short
            self.error_nodes = error_nodes
            # print(self.chain)
