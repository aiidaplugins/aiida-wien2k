import os
import ase
import ase.io

def getfilename():
    path=os.getcwd()
    filename=path.split("/")[-1]
    return filename

def writestruct(structure,sgroup=False,filename=None):
    if filename is None:
        filename=getfilename()
    ase.io.write(filename+".struct",structure)
    if(sgroup):
        os.system('x sgroup -f '+filename+'; cp '+filename+'.struct_sgroup '+filename+'.struct')

def grep(key,filename=None):
    if filename is None:
        filename=getfilename()
    #Aaarrrggghhhh
    if(key==":ENE"): 
        col1=39;col2=61
    elif(key==":VOL"): 
        col1=26;col2=40
    f = open(filename + '.scf', 'r')
    pip = f.readlines()
    value = []
    for line in pip:
        if line[0:len(key)] == key:
            value.append(float(line[col1:col2]) )
    return value
