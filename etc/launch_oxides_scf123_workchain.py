from aiida.engine import submit
from aiida import orm
from aiida_wien2k.workflows.scf123_workchain import Wien2kScf123WorkChain
import time
from aiida.plugins.factories import WorkflowFactory
from aiida.schedulers.datastructures import NodeNumberJobResource

# Setting up crystal structure(s)
elements_all = ['H', \
        'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', \
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', \
        'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', \
        'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', \
        'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', \
            'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', \
        'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', \
            'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
#elements = elements_all[0:36] # H ... Kr
#elements = elements_all[36:65] # Rb ... Tb
#elements = elements_all[65: ] # Dy ... Og
elements = elements_all
configurations = ['X2O', 'XO', 'X2O3', 'X2O5', 'XO2', 'XO3']
chemformulas_compleated = []
res = NodeNumberJobResource(num_machines=1, num_mpiprocs_per_machine=1, num_cores_per_mpiproc=1) # set resources
for node in Group.get(label='commonwf-oxides/set2/structures').nodes:
    aiida_structure = node # get structure of SiO2
    element = aiida_structure.extras['element'] # chemical element X
    configuration = aiida_structure.extras['configuration'] # X2O, XO2, etc.
    formula = element + '-' + configuration # H-XO3
    if ( (element in elements) and (configuration in configurations) ):
        print(node.extras) # info about chem. composition
        chemformula = aiida_structure.get_formula()
        if (chemformula in chemformulas_compleated):
            continue # skip iteration
        # run SCF123 workchain
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
        result = submit(Wien2kScf123WorkChain, aiida_structure=aiida_structure,\
                code=code, inpdict=inpdict)
        print('result=', result)
        time.sleep(15) # Delay for 15 second
