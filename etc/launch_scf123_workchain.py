from aiida.engine import submit, run
from aiida import orm
from ase.spacegroup import crystal
from aiida_wien2k.workflows.scf123_workchain import Wien2kScf123WorkChain
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
code = orm.load_code(label='wien2k-run123_lapw@localhost')
inpdict = orm.Dict(dict={\
        '-i': '100',\
        '-red': '3',\
        '-ec': '0.000001',\
        '-cc': '0.00003',\
        '-hdlo': True,\
        '-fermit': '0.0045',\
        '-nokshift': True,\
        '-deltak': '0.021'
}) # run123_lapw [param]
res = NodeNumberJobResource(num_machines=1,\
        num_mpiprocs_per_machine=1, num_cores_per_mpiproc=1) # set resources
result = submit(Wien2kScf123WorkChain, aiida_structure=aiida_structure,\
        code=code, inpdict=inpdict)
print('result=', result)
