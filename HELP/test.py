
'coding:-*utf-8*-'

from fix import run_one,norm,normal_py


    
if __name__ == '__main__':
    
    with open('example/install_1.txt','r',encoding='utf-8') as f:
        tasks = f.read().split('\n')
    
    for task in tasks:
        print('==========================')
        tmp = task.split('#')
        library = (norm(tmp[0]),tmp[1])
        Sym = normal_py(tmp[2])    
        run_one(library,Sym)
        print('==========================')
        
