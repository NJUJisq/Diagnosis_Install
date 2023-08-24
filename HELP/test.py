
'coding:-*utf-8*-'
import os
import json
from fix import run_one
import time


def norm(s):
    return s.lower().replace('-','_')  


if __name__ == '__main__':
    
    with open('example/install_1.txt','r',encoding='utf-8') as f:
        tasks = f.readlines()
    
    for task in tasks:
        tmp = task.split('#')
        library = (norm(tmp[0]),tmp[1])
        Sym = tmp[2]    
        run_one(library,Sym)
        
