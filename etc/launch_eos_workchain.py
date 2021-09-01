import numpy as np
from aiida.engine import submit, run
from aiida import orm
from ase.spacegroup import crystal
from aiida_wien2k.workflows.eos_workchain import Wien2kEosWorkChain
from aiida.schedulers.datastructures import NodeNumberJobResource

# Setting up crystal structure

# ASE structure
ase_structure = crystal('Si', [(0, 0, 0)], spacegroup=227,\
        cellpar=[5.43, 5.43, 5.43, 90, 90, 90])
# ase_structure = crystal('Si', [(0, 0, 0)], spacegroup=227,\
#         cellpar=[5.43/2, 5.43/2, 5.43/2, 90, 90, 90])
# ASE -> AiiDA structure
aiida_structure = orm.StructureData(ase=ase_structure)

# run workchain
code1 = orm.load_code(label='wien2k-x-sgroup@localhost')
code2 = orm.load_code(label='wien2k-init_lapw@localhost')
code3 = orm.load_code(label='wien2k-run_lapw@localhost')
code4 = orm.load_code(label='wien2k-x-optimize@localhost')
code5 = orm.load_code(label='wien2k-run_lapw_clmextrapol@localhost')
inpdict1 = orm.Dict(dict={}) # x sgroup [param]
inpdict2 = orm.Dict(dict={'-red':'3', '-numk': '700'}) # init_lapw -b [param]
inpdict3 = orm.Dict(dict={'-i': '100'}) # run_lapw [param]
inparr4 = orm.ArrayData()
inparr4.set_array('dvolumes', np.array([-6,-4,-2,2,4,6])) # volme change in % (exclude 0)
res = NodeNumberJobResource(num_machines=1, num_mpiprocs_per_machine=1, num_cores_per_mpiproc=1) # set resources
result = submit(Wien2kEosWorkChain, aiida_structure=aiida_structure,\
        code1=code1, code2=code2, code3=code3, code4=code4, code5=code5,\
        inpdict1=inpdict1, inpdict2=inpdict2, inpdict3=inpdict3, inparr4=inparr4)
print('result=', result)
